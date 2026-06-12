release: python manage.py migrate --no-input
web: gunicorn ChroniCare.wsgi:application --bind 0.0.0.0:$PORT --workers 2
worker: celery -A ChroniCare worker -l info
beat: celery -A ChroniCare beat -l info
