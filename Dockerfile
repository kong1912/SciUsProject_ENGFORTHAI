FROM python:3.9.7-stretch

WORKDIR /app
ADD . /app

RUN pip install -r requirements.txt

CMD ["uwsgi", "app.ini"]
