import os
import json
import time
import logging
from datetime import datetime, timezone

import requests
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceNotFoundError
timestamp = datetime.now(timezone.utc).isoformat()
# ==========================================================
# Configuration
# ==========================================================
URLS = {
    "Web App": "https://hi.com",
    "API": "https://hi.com/api"
}


CHECK_INTERVAL = 900  # 5 Minutes
STORAGE_ACCOUNT_NAME = os.getenv("AZURE_STORAGE_ACCOUNT_NAME","testfilesdev")
STORAGE_ACCOUNT_KEY = os.getenv("AZURE_STORAGE_ACCOUNT_KEY")
STORAGE_CONTAINER_NAME = os.getenv("AZURE_STORAGE_CONTAINER","devops")

FILE_NAME = os.getenv("FILE_NAME","dns_status.json")

FOLDER_NAME = os.getenv("FOLDER_NAME","dns_status")

BLOB_PATH = f"{FOLDER_NAME}/{FILE_NAME}"

# ==========================================================
# Logger
# ==========================================================

def setup_logger():
    logger = logging.getLogger("dns_monitor")

    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    file_handler = logging.FileHandler("dns_monitor.log")
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


logger = setup_logger()

# ==========================================================
# Functions
# ==========================================================

def check_endpoint(url):
    """
    Check URL health status.
    200 and 401 => Operational
    Others => Non-Operational
    """

    try:
        logger.info(f"Checking URL: {url}")

        response = requests.get(
            url,
            timeout=30,
            allow_redirects=True
        )

        status = (
            "Operational"
            if response.status_code in [200, 403]
            else "Non-Operational"
        )

        result = {
            "status": status,
            "code": response.status_code,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        logger.info(
            f"URL={url}, Status={status}, Code={response.status_code}"
        )

        return result

    except Exception as ex:
        logger.exception(f"Request failed for {url}")

        return {
            "status": "Non-Operational",
            "code": 0,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(ex)
        }


def get_existing_json(blob_service_client):
    """
    Download existing JSON from blob.
    If file does not exist, return empty dict.
    """

    try:
        blob_client = blob_service_client.get_blob_client(
            container=STORAGE_CONTAINER_NAME,
            blob=BLOB_PATH
        )

        content = blob_client.download_blob().readall()

        logger.info(
            f"Successfully downloaded existing blob {BLOB_PATH}"
        )

        return json.loads(content)

    except ResourceNotFoundError:
        logger.info(
            f"Blob {BLOB_PATH} not found. Creating new file."
        )
        return {}

    except Exception as ex:
        logger.exception(
            f"Error downloading blob {BLOB_PATH}: {ex}"
        )
        raise


def update_json(existing_data, service_name, result):

    date_key = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    existing_data.setdefault(service_name, {})
    existing_data[service_name].setdefault(date_key, [])

    existing_data[service_name][date_key].append(result)

    return existing_data



def upload_json(blob_service_client, data):
    """
    Upload updated JSON to Azure Blob Storage.
    """

    try:
        blob_client = blob_service_client.get_blob_client(
            container=STORAGE_CONTAINER_NAME,
            blob=BLOB_PATH
        )

        blob_client.upload_blob(
            json.dumps(data, indent=4),
            overwrite=True
        )

        logger.info(
            f"Successfully uploaded blob {BLOB_PATH}"
        )

    except Exception as ex:
        logger.exception(
            f"Failed uploading blob {BLOB_PATH}: {ex}"
        )
        raise


def run_health_checks(blob_service_client):

    logger.info("Starting health check cycle")

    existing_data = get_existing_json(blob_service_client)

    for service_name, url in URLS.items():

        result = check_endpoint(url)

        update_json(
            existing_data,
            service_name,
            result
        )

    upload_json(
        blob_service_client,
        existing_data
    )

    logger.info("Health check cycle completed")


# ==========================================================
# Main Function
# ==========================================================

def main():

    logger.info("DNS Health Monitor Started")

    if not STORAGE_ACCOUNT_KEY:
        raise ValueError(
            "AZURE_STORAGE_ACCOUNT_KEY environment variable is missing."
        )

    blob_service_client = BlobServiceClient(
        account_url=(
            f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net"
        ),
        credential=STORAGE_ACCOUNT_KEY
    )

    while True:

        try:
            run_health_checks(blob_service_client)

        except Exception as ex:
            logger.exception(
                f"Unexpected error occurred: {ex}"
            )

        logger.info(
            f"Sleeping for {CHECK_INTERVAL} seconds"
        )

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()