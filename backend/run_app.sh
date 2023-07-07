cd foodgram || exit
python manage.py migrate;
python manage.py import_csv;
python manage.py collectstatic --noinput;
# cp -r /app/collected_static/. /backend_static/static/
gunicorn -b 0:8000 foodgram.wsgi;
