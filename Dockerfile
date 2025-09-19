FROM bbernhard/signal-cli-rest-api:latest

RUN apk add --no-cache python3 py3-pip
WORKDIR /app

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY MultiGroupMsgReader.py config.yaml .

# Start both services
CMD ["sh", "-c", "signal-cli-rest-api & python3 MultiGroupMsgReader.py"]
