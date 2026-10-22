FROM gcr.io/google.com/cloudsdktool/google-cloud-cli:stable
RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-pip python3-venv && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY inventory/ /app/inventory/
COPY cloudrun/ /app/cloudrun/
RUN python3 -m venv /opt/venv && /opt/venv/bin/pip install --no-cache-dir -r /app/cloudrun/requirements.txt
ENV PATH="/opt/venv/bin:$PATH"
ENTRYPOINT ["python3", "/app/cloudrun/job.py"]
