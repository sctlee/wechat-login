FROM python:2.7.9

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/

RUN pip install -r requirements.txt

COPY . /usr/src/app

EXPOSE 5200

CMD [ "gunicorn","--max-requests","3000","--access-logfile","-", "--error-logfile","-","-b","0.0.0.0:5200","app_runner:app"  ]
