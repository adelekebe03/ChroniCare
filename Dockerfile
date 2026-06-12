FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --no-input --clear

CMD ["gunicorn", "ChroniCare.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2"]
