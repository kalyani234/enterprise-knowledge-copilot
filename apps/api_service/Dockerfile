FROM python:3.11-slim

WORKDIR /app

# system deps (small but enough for most python wheels)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# install python deps
COPY apps/api_service/requirements.txt /app/apps/api_service/requirements.txt
RUN pip install --no-cache-dir -r /app/apps/api_service/requirements.txt

# copy project code
COPY . /app

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

EXPOSE 8000

CMD ["uvicorn", "apps.api_service.main:app", "--host", "0.0.0.0", "--port", "8000"]
