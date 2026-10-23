FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY meteo_stats/ meteo_stats/

ENV DATABASE_URL=""
CMD ["python", "-m", "meteo_stats.cli", "villes"]
