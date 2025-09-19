FROM bbernhard/signal-cli-rest-api:latest

# Install Python & pip (Debian-based image)
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY MultiGroupMsgReader.py .

# Copy linked account (from Render Secret Files)
COPY /etc/secrets/signal-data /home/.local/share/signal-cli

# Start both services: signal-cli-rest-api + Python script
CMD ["sh", "-c", "signal-cli-rest-api & python3 MultiGroupMsgReader.py"]
