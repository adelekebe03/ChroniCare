FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --no-input --clear

# Au démarrage : migrate (idempotent) puis lance gunicorn.
# Shell form nécessaire pour l'expansion de $PORT par le shell.
CMD ["sh", "-c", "python manage.py migrate --no-input && gunicorn ChroniCare.wsgi:application --bind 0.0.0.0:$PORT --workers 2"]
