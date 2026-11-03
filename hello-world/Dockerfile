# Use Ubuntu 22.04
FROM ubuntu:24.04

# Install Java and network utilities
RUN apt-get update && apt-get install -y \
        openjdk-17-jdk \
        curl \
        wget \
        net-tools \
        iputils-ping \
   && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m appuser
# Copy your application
COPY target/hello-world-1.38.jar /app/

WORKDIR /app
# Fix permissions
RUN chown -R appuser:appuser /app
# Switch to non-root user
USER appuser
EXPOSE 3648

ENTRYPOINT ["java", "-jar", "/app/hello-world-1.38.jar"]