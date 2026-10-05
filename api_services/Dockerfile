FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY api_services/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app/api_services
COPY api_services/ .

EXPOSE 8081
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8081"]