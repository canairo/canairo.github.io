FROM debian:stable-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        python3 \
        python3-pip \
        make \
        libc6-dev \
        && rm -rf /var/lib/apt/lists/*

# Flask app
WORKDIR /app

COPY app.py /app/app.py
COPY prots.py /app/prots.py
COPY requirements.txt /app/requirements.txt

RUN pip3 install --no-cache-dir -r requirements.txt --break-system-packages

# Sandbox directory
RUN mkdir /sandbox
RUN chmod 777 /sandbox

# Add flag
RUN echo "incredible! wow! you've managed to recover a totally hypothetical flag" > /flag.txt
RUN chmod 444 /flag.txt

EXPOSE 5000

CMD ["python3", "app.py"]

