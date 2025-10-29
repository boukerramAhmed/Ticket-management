FROM python:3.13-slim
WORKDIR /src/

COPY requirements.txt  /src/requirements.txt

RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r /src/requirements.txt

COPY ./app /src/app

EXPOSE 8000
# Commande par défaut
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]