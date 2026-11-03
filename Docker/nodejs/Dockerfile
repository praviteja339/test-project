FROM node:22.14.0
WORKDIR /usr/src/app
RUN groupadd --gid 2001 nodeuser && useradd --home-dir /home/nodeuser --create-home --uid 1001 --gid 2001 --shell /bin/sh --skel /dev/null nodeuser
RUN chown -R nodeuser:nodeuser /home/nodeuser && chown -R nodeuser:nodeuser /usr/src/app
USER nodeuser
