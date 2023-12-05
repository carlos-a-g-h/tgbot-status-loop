FROM python:3.9.8-slim-bullseye

WORKDIR /mybot

COPY . .

RUN apt update;apt install -yy apache2;pip install req.txt

CMD ["bash","run.sh"]
