FROM python:3.9.2

WORKDIR /online-course-manager

ENV FLASK_APP=flaskr/app

COPY requirements.txt requirements.txt

# upgrade pip
RUN pip3 install --upgrade pip

# install pip dependencies
RUN pip3 install -r requirements.txt

# install waitress
RUN pip3 install waitress 

COPY flaskr .
COPY .env .env

CMD [ "waitress-serve", "--call", "app:create_app"]