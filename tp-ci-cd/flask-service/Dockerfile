# flask-service/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Installer netcat pour attendre MySQL
RUN apt-get update && apt-get install -y netcat && rm -rf /var/lib/apt/lists/*

# Copier requirements et installer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code
COPY . .

# Copier l’entrypoint pour attendre la DB
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

EXPOSE 5000

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["python", "app.py"]
