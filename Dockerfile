FROM python:3.11-slim

WORKDIR /app

# Force rebuild - Updated 2025-08-08
ENV REBUILD_TIMESTAMP=20250808_3
ENV CACHE_BREAKER=v3

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["python", "-m", "uvicorn", "api.index:app", "--host", "0.0.0.0", "--port", "8080"]