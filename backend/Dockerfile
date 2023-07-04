FROM python:3.9-slim

# RUN apt-get update &&\
#     apt-get upgrade -y &&\
#     apt-get install -y libpq-dev gcc netcat

WORKDIR /app

RUN pip install gunicorn==20.1.0

COPY requirements.txt .

RUN pip install -U pip &&\
    pip install -r requirements.txt --no-cache-dir

COPY . .

RUN chmod +x run_app.sh
ENTRYPOINT [ "/app/run_app.sh" ]
# CMD ["gunicorn", "--bind", "0.0.0.0:8000", "kittygram_backend.wsgi"]