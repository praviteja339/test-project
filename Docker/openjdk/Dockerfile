FROM --platform=linux/amd64 eclipse-temurin:25-jdk-jammy

ENV DEBIAN_FRONTEND=noninteractive
ENV CHROME_BIN=/usr/bin/google-chrome
ENV PATH="${PATH}:${CHROME_BIN}"

# Install Chrome and dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    curl \
    unzip \
    fonts-liberation \
    xdg-utils \
    lsb-release \
    --no-install-recommends && \
    # Add Google Chrome key
    wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | \
    gpg --dearmor -o /usr/share/keyrings/google-linux.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-linux.gpg] http://dl.google.com/linux/chrome/deb/ stable main" \
    > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && apt-get install -y google-chrome-stable && \
    google-chrome --version && \
    rm -rf /var/lib/apt/lists/*

# --- Build Leptonica 1.85.0 ---
RUN apt-get update && apt-get install -y git build-essential autoconf automake libtool pkg-config \
    libjpeg-dev libpng-dev libtiff-dev zlib1g-dev && \
    git clone --branch 1.85.0 https://github.com/DanBloomberg/leptonica.git && \
    cd leptonica && ./autogen.sh && ./configure && make -j$(nproc) && make install && cd .. && rm -rf leptonica

# --- Build Tesseract 5.5.0 ---
RUN git clone --branch 5.5.0 https://github.com/tesseract-ocr/tesseract.git && \
    cd tesseract && ./autogen.sh && ./configure && make -j$(nproc) && make install && ldconfig && cd .. && rm -rf tesseract

# Create non-root user
RUN mkdir app
RUN groupadd --gid 2001 javauser && useradd --home-dir /home/javauser --create-home --uid 1001 --gid 2001 --shell /bin/sh --skel /dev/null javauser
RUN chown -R javauser:javauser /app
USER javauser
