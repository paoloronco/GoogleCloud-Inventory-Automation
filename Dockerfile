FROM gcr.io/google.com/cloudsdktool/google-cloud-cli:stable
RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-venv && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY inventory/ /app/inventory/
COPY cloudrun/ /app/cloudrun/
ENTRYPOINT ["python3", "/app/cloudrun/job.py"]
