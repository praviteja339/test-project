import os
import subprocess
import logging
import threading
import time
import json
import requests
from datetime import datetime, timedelta, timezone
from azure.identity import ClientSecretCredential, DefaultAzureCredential
from azure.keyvault.certificates import CertificateClient
from azure.storage.fileshare import ShareServiceClient

# -----------------------------
# LOGGING
# -----------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(threadName)s | %(message)s"
)

# -----------------------------
# CONFIG
# -----------------------------
TEST_VAULT = "https://testcerts.vault.azure.net/"
TEST_DEV_VAULT = "https://testcerts-dev.vault.azure.net/"

KEY_VAULTS = [
    TEST_VAULT,
    TEST_DEV_VAULT
]

CHECK_WINDOW_MINUTES = 1440

APP_PROJECT = os.getenv("APP_PROJECT")
SSL_PROJECT = os.getenv("SSL_PROJECT")
ORG = os.getenv("AZURE_DEVOPS_ORG")

AZDO_PAT = os.getenv("AZDO_PAT")

SRE_PIPELINE = os.getenv("PIPELINE_NAME")
SSL_PIPELINE = os.getenv("SSL_CERT_PIPELINE")

# Early validation of required env vars
required_vars = {
    "AZDO_PAT": AZDO_PAT,
    "AZURE_DEVOPS_ORG": ORG,
    "APP_PROJECT": APP_PROJECT,
    "SSL_PROJECT": SSL_PROJECT,
    "PIPELINE_NAME": SRE_PIPELINE,
    "SSL_CERT_PIPELINE": SSL_PIPELINE,
}
missing = [k for k, v in required_vars.items() if not v]
if missing:
    raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")
# -----------------------------
# CERT  PIPELINE MAP
# -----------------------------
CERT_PIPELINE_MAP = {
    "testpricing": {
        "uat": ["test-go-cd-uat"],#pipeline names#
        "prod": ["hi-ui-cd-prod", "hi-ui-cd-prod", "ti-cd-prod", "test-go-cd-prod"],
        "stage": ["hi-ui-cd-stage"],
        "test": ["hi-ui-cd-test", "hi-ui-cd-test"],
        "dev": ["hi-ui-cd-dev","hi-ui-cd-dev","test-go-cd-dev"],
        "qa": ["hi-ui-cd-qa","test-go-cd-qa","hi-ui-cd-qa"],
    },
    "test": {
        "prod": ["hi-cd-production", "ti-cd-prod"],
        "ca": ["helo-cd-test-analysis"],
        "stage": ["helo-cd-stage", ],
        "test": ["helo-cd-test"],
        "uat": ["helo-cd-uat", "ti-cd-uat", "te-cd-uat"],
        "dev": ["test-cd-dev","helo-ui-cd-dev","co-cd-dev"],
        "qa": ["helo-cd-qa","ti-ui-cd-qa","co-cd-qa"]
    },
    "hi-uat": {
        "uat": ["hitest-ui-cd-uat"]
    },
    "hi-hi": {
        "hi": ["hi-ui-cd-hi"]
    },
    "hi-uat": {
        "uat": ["uat-ui-cd-uat"]
    },
    "hica": {
        "ca": ["hi-ui-cd-ca"]
    },
    "portal-dev": {
        "dev": ["hi-cd-dev"]
    },
    "portal-qa": {
        "qa": ["hi-cd-qa"]
    }

}

# -----------------------------
# AUTH
# -----------------------------
credential = DefaultAzureCredential()

#  EMAIL credential
email_credential = ClientSecretCredential(
    tenant_id=os.getenv("AZURE_TENANT_ID"),
    client_id=os.getenv("GraphClientId"),
    client_secret=os.getenv("GraphClientSecret")
)

# -----------------------------
# STORAGE
# -----------------------------
STORAGE_ACCOUNT_NAME = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
STORAGE_ACCOUNT_KEY = os.getenv("AZURE_STORAGE_ACCOUNT_KEY")
FILE_SHARE_NAME = os.getenv("AZURE_FILE_SHARE", "devops-shared")

if not STORAGE_ACCOUNT_NAME or not STORAGE_ACCOUNT_KEY:
    raise Exception("Missing storage account configuration")

connection_string = (
    f"DefaultEndpointsProtocol=https;"
    f"AccountName={STORAGE_ACCOUNT_NAME};"
    f"AccountKey={STORAGE_ACCOUNT_KEY};"
    f"EndpointSuffix=core.windows.net"
)

share_client = ShareServiceClient.from_connection_string(
    connection_string
).get_share_client(FILE_SHARE_NAME)

FILE_NAME = "cert_state.json"
FOLDER_NAME = "cert_json"


# -----------------------------
# COMMAND
# -----------------------------
def run_cmd(cmd, pat):
    env = os.environ.copy()
    env["AZURE_DEVOPS_EXT_PAT"] = pat

    logging.info(f"Running command: {' '.join(cmd)}")

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        env=env
    )

    if result.returncode != 0:
        logging.error(result.stderr)
        raise Exception(result.stderr)

    return result.stdout


# -----------------------------
# PIPELINE
# -----------------------------
def get_pipeline_id(pipeline_name, pat, project):
    """Resolve pipeline name → pipeline ID."""
    logging.info(f"Resolving pipeline ID for {pipeline_name}")
    data = json.loads(run_cmd([
        "az", "pipelines", "list",
        "--name", pipeline_name,
        "--org", ORG,
        "--project", project,
        "--output", "json"
    ], pat))

    if not data:
        logging.warning(f"Pipeline not found: {pipeline_name}")
        return None

    # az pipelines list returns a list; take the first match
    return data[0].get("id")


def get_latest_run(pipeline_name, pat, project):
    """Return the most recent run of a pipeline (any result), or None."""
    pipeline_id = get_pipeline_id(pipeline_name, pat, project)
    if not pipeline_id:
        return None

    logging.info(f"Looking up latest run for {pipeline_name} (id={pipeline_id})")
    data = json.loads(run_cmd([
        "az", "pipelines", "runs", "list",
        "--pipeline-ids", str(pipeline_id),
        "--org", ORG,
        "--project", project,
        "--top", "1",
        "--output", "json"
    ], pat))

    if not data:
        logging.warning(f"No runs found for {pipeline_name}")
        return None
    return data[0]

def trigger_pipeline(name, pat, project):
    logging.info(f"Triggering pipeline: {name}")

    last_run = get_latest_run(name, pat, project)

    cmd = [
        "az", "pipelines", "run",
        "--name", name,
        "--org", ORG,
        "--project", project,
        "--output", "json"
    ]

    if last_run:
        branch = last_run.get("sourceBranch")       # e.g. refs/heads/main
        commit = last_run.get("sourceVersion")      # exact commit SHA
        result = last_run.get("result")             # succeeded / failed / canceled ...

        if branch:
            cmd.extend(["--branch", branch])
        if commit:
            cmd.extend(["--commit-id", commit])

        logging.info(
            f"Using latest run (result={result}) → "
            f"branch={branch}, commit={commit}"
        )
    else:
        logging.warning(
            f"No previous runs found for {name}. "
            "Using pipeline default branch."
        )

    data = json.loads(run_cmd(cmd, pat))
    run_id = data.get("id")
    logging.info(f"{name} → RunID={run_id}")
    return run_id


def wait_pipeline(run_id, pat, project):
    logging.info(f"Waiting for pipeline {run_id}")

    while True:
        data = json.loads(run_cmd([
            "az", "pipelines", "runs", "show",
            "--id", str(run_id),
            "--org", ORG,
            "--project", project,
            "--output", "json"
        ], pat))

        status = data.get("status")
        result = data.get("result")

        logging.info(f"Run {run_id}: {status} / {result}")

        if status == "completed":
            return result

        time.sleep(30)

# PIPELINE RESOLUTION
# -----------------------------
def get_pipelines_for_cert(cert):
    env_map = CERT_PIPELINE_MAP.get(cert, {})
    pipelines = []

    for env, plist in env_map.items():
        logging.info(f"{cert} → {env} → {plist}")
        pipelines.extend(plist)

    return pipelines

# -----------------------------
# APP PIPELINES
# -----------------------------
def trigger_app_pipelines(cert_updates):

    run_ids = []
    processed = set()

    for update in cert_updates:

        cert = update["cert"]

        if cert in processed:
            continue

        processed.add(cert)

        pipelines = get_pipelines_for_cert(cert)

        for p in pipelines:

            run_id = trigger_pipeline(
                p,
                AZDO_PAT,
                APP_PROJECT
            )

            run_ids.append({
                "cert": cert,
                "pipeline": p,
                "run_id": run_id
            })

    results = []

    for item in run_ids:

        result = wait_pipeline(
            item["run_id"],
            AZDO_PAT,
            APP_PROJECT
        )

        results.append({
            "cert": item["cert"],
            "pipeline": item["pipeline"],
            "run_id": item["run_id"],
            "result": result
        })

    return results
# -----------------------------
# STATE
# -----------------------------
def load_state():
    try:
        file = share_client.get_file_client(f"{FOLDER_NAME}/{FILE_NAME}")
        data = file.download_file().readall()
        return json.loads(data.decode())
    except:
        return {}


def save_state(state):
    file = share_client.get_file_client(f"{FOLDER_NAME}/{FILE_NAME}")

    try:
        file.delete_file()
    except:
        pass

    file.upload_file(json.dumps(state).encode())


# -----------------------------
# KEY VAULT
# -----------------------------
def check_vault(vault_url, state):
    """
    Check certificates updated recently and detect newly updated certificates.
    Returns list of dicts: [{"vault": ..., "cert": ...}, ...]
    """
    updates_found = []
    try:
        client = CertificateClient(
            vault_url=vault_url,
            credential=credential
        )

        now = datetime.now(timezone.utc)
        threshold = now - timedelta(minutes=CHECK_WINDOW_MINUTES)

        logging.info(f"Checking vault: {vault_url}")
        certs = list(client.list_properties_of_certificates())
        logging.info(f"Total certificates found in {vault_url}: {len(certs)}")

        for cert in certs:
            logging.info(f"Certificate checked: {cert.name}")

            state_key = f"{vault_url}:{cert.name}"

            # Read previous state BEFORE overwriting
            previous_state = state.get(state_key, {})
            last_seen = previous_state.get("updated_on")

            logging.info(
                f"Comparing cert={cert.name}, "
                f"current={cert.updated_on}, "
                f"last_seen={last_seen}"
            )

            # Detect updates
            if cert.updated_on:
                should_trigger = False

                if not last_seen:
                    # First time we see this cert – only trigger if recent
                    if cert.updated_on >= threshold:
                        should_trigger = True
                        logging.info(
                            f"New certificate detected: {cert.name} | "
                            f"Updated: {cert.updated_on}"
                        )
                else:
                    try:
                        last_seen_dt = datetime.fromisoformat(last_seen)
                        if (cert.updated_on > last_seen_dt and
                                cert.updated_on >= threshold):
                            should_trigger = True
                            logging.info(
                                f"Certificate update detected: {cert.name} | "
                                f"Previous: {last_seen_dt} | "
                                f"Current: {cert.updated_on}"
                            )
                    except Exception as parse_error:
                        logging.error(
                            f"Failed to parse stored timestamp "
                            f"for cert {cert.name}: {parse_error}"
                        )

                if should_trigger:
                    updates_found.append({
                        "vault": vault_url,
                        "cert": cert.name
                    })

            # Always save the latest rich state AFTER comparison
            state[state_key] = {
                "vault": vault_url,
                "certificate_name": cert.name,
                "updated_on": (
                    cert.updated_on.isoformat() if cert.updated_on else None
                ),
                "enabled": cert.enabled,
                "expires_on": (
                    cert.expires_on.isoformat() if cert.expires_on else None
                ),
                "created_on": (
                    cert.created_on.isoformat() if cert.created_on else None
                ),
                "tags": dict(cert.tags) if cert.tags else None,
            }

        if not updates_found:
            logging.info(
                f"No new certificate updates detected in vault {vault_url}"
            )

        return updates_found

    except Exception as e:
        logging.error(f"Error while checking vault {vault_url}: {e}")
        return []

# EMAIL

def build_pipeline_url(project, run_id):
    return f"{ORG}/{project}/_build/results?buildId={run_id}&view=results"


def send_email(certs, pipelines, sre_status, ssl_status, sre_id, ssl_id):
    logging.info("Sending email...")

    try:
        #  Overall status
        overall_status = "Succeeded"
        header_color = "lightgreen"

        sre_ok = sre_status.lower() in ["succeeded", "skipped"]

        if not sre_ok or ssl_status != "succeeded" or \
                any(p["result"] != "succeeded" for p in pipelines):
            overall_status = "Failed"
            header_color = "red"

        # Links
        sre_url = (
            build_pipeline_url(APP_PROJECT, sre_id)
            if sre_id
            else "#"
        )
        ssl_url = build_pipeline_url(SSL_PROJECT, ssl_id)

        # Start HTML
        body = f"""
        <html>
          <style>
            table, th, td {{
                border:1px solid black;
                border-collapse: collapse;
                padding:6px;
            }}
          </style>
          <body>

            <h2>SSL Automation status is 
              <span style='color:{header_color};'>{overall_status}</span>
            </h2>

            <p>Hi There!!!</p>

            <table style="width:80%">
              <tr>
                <th colspan="2" style="background-color:{header_color};">
                  BUILD SUMMARY
                </th>
              </tr>

              <tr>
                <th>Job</th>
                <td>SSL Certificate Automation</td>
              </tr>

              <tr>
                <th>Certificates</th>
                <td>{', '.join(certs)}</td>
              </tr>

              <tr>
                <th>Status</th>
                <td>{overall_status}</td>
              </tr>

              <tr>
                <th>Triggered By</th>
                <td>Automation Script</td>
              </tr>
            </table>

            <br>

            <h3>Pipeline Execution Details</h3>

            <table style="width:80%">
              <tr>
                <th>Stage</th>
                <th>Pipeline</th>
                <th>Status</th>
              </tr>
        """

        #  SRE row
        sre_color = "green" if sre_status == "succeeded" else "red"
        body += f"""
            <tr>
              <td>SRE</td>
              <td>
                <a href="{sre_url}" style="color:{sre_color}; font-weight:bold;">
                  {SRE_PIPELINE}
                </a>
              </td>
              <td style="color:{sre_color}; font-weight:bold;">
                {sre_status}
              </td>
            </tr>
        """

        #  APP rows
        for p in pipelines:
            app_url = build_pipeline_url(APP_PROJECT, p["run_id"])
            app_color = "green" if p["result"] == "succeeded" else "red"

            body += f"""
            <tr>
              <td>Application</td>
              <td>
                <a href="{app_url}" style="color:{app_color}; font-weight:bold;">
                  {p['pipeline']}
                </a>
              </td>
              <td style="color:{app_color}; font-weight:bold;">
                {p['result']}
              </td>
            </tr>
            """

        #  SSL row
        ssl_color = "green" if ssl_status == "succeeded" else "red"
        body += f"""
            <tr>
              <td>SSL</td>
              <td>
                <a href="{ssl_url}" style="color:{ssl_color}; font-weight:bold;">
                  {SSL_PIPELINE}
                </a>
              </td>
              <td style="color:{ssl_color}; font-weight:bold;">
                {ssl_status}
              </td>
            </tr>
        """

        body += """
            </table>
            <br><br>
            <p style="font-family: Arial, sans-serif;">
                Regards,<br>
                <strong>DevOps Team</strong>
            </p>
          </body>
        </html>
        """

        subject = f"SSL Automation {overall_status}: {', '.join(certs)}"

        #  Send email
        token = email_credential.get_token("https://graph.microsoft.com/.default")

        response = requests.post(
            f"https://graph.microsoft.com/v1.0/users/{os.getenv('EMAIL_FROM')}/sendMail",
            headers={
                "Authorization": f"Bearer {token.token}",
                "Content-Type": "application/json"
            },
            json={
                "message": {
                    "subject": subject,
                    "body": {
                        "contentType": "HTML",
                        "content": body
                    },
                    "toRecipients": [
                        {
                            "emailAddress": {
                                "address": os.getenv("EMAIL_TO")
                            }
                        }
                    ]
                },
                "saveToSentItems": False
            }
        )

        if response.status_code not in (200, 202):
            logging.error(f"Email failed: {response.text}")
        else:
            logging.info(" Email sent successfully")

    except Exception as e:
        logging.error(f"Email error: {e}", exc_info=True)

# MAIN

def main():
    logging.info("STARTING PROCESS")

    state = load_state()
    updates = []

    for vault in KEY_VAULTS:
        updates.extend(check_vault(vault, state))

    save_state(state)

    unique_updates = []
    seen = set()

    for update in updates:

        key = (
            update["vault"],
            update["cert"]
        )

        if key not in seen:
            seen.add(key)
            unique_updates.append(update)

    updates = unique_updates

    if not updates:
        logging.info("No updates found")
        return

    logging.info(f"Updates found: {updates}")
    test_updates = [
        u for u in updates
        if u["vault"] == TEST_VAULT
    ]

    test_dev_updates = [
        u for u in updates
        if u["vault"] == TEST_DEV_VAULT
    ]
    app_results = []

    sre_id = None
    sre_result = "Skipped"

    # test-certs vault updates
    if test_updates:

        logging.info(
            "Production vault certificate update detected."
        )

        sre_id = trigger_pipeline(
            SRE_PIPELINE,
            AZDO_PAT,
            APP_PROJECT
        )

        sre_result = wait_pipeline(
            sre_id,
            AZDO_PAT,
            APP_PROJECT
        )

        if sre_result.lower() == "succeeded":

            app_results.extend(
                trigger_app_pipelines(
                    test_updates
                )
            )
        else:
            logging.error(
                "SRE pipeline failed. Skipping APP deployments."
            )

    # DEV vault updates

    if test_dev_updates:

        logging.info("DEV vault certificate update detected.")

        logging.info("Skipping SRE Pipeline")

        app_results.extend(trigger_app_pipelines(test_dev_updates))
    # -----------------------------
    # SSL Pipeline – debug + trigger
    # -----------------------------
    logging.info("=" * 60)
    logging.info("SSL PIPELINE DEBUG INFO")
    logging.info(f"ORG            = {ORG!r}")
    logging.info(f"SSL_PROJECT    = {SSL_PROJECT!r}")
    logging.info(f"SSL_PIPELINE   = {SSL_PIPELINE!r}")
    logging.info(f"APP_PROJECT    = {APP_PROJECT!r}")
    logging.info(f"AZDO_PAT set?  = {bool(AZDO_PAT)}")
    logging.info("=" * 60)

    if not SSL_PROJECT:
        raise RuntimeError(
            "SSL_PROJECT environment variable is empty or not set. "
            "Cannot trigger SSL pipeline."
        )
    if not SSL_PIPELINE:
        raise RuntimeError(
            "SSL_CERT_PIPELINE environment variable is empty or not set. "
            "Cannot trigger SSL pipeline."
        )

    # SSL Pipeline

    ssl_id = trigger_pipeline(SSL_PIPELINE,AZDO_PAT,SSL_PROJECT)

    ssl_result = wait_pipeline(ssl_id,AZDO_PAT,SSL_PROJECT)

    # 4. EMAIL
    send_email([u["cert"] for u in updates],app_results,sre_result,ssl_result,sre_id,ssl_id)

    logging.info("COMPLETED SUCCESSFULLY")

if __name__ == "__main__":
    main()
