FROM python:3-alpine

# PsycoPG is the driver for PostgreSQL installations
#  (used through SQLAlchemy.)
ADD requirements.txt /app/requirements.txt

RUN apk add --no-cache git libpq postgresql-dev build-base \
  && pip install -r /app/requirements.txt \
  && apk del git build-base postgresql-dev

ADD . /app
RUN pip install -e /app

# Bridge database (projects, users, ...)
VOLUME /root/.local/share/plaza/bridges/gitlab/db.sqlite

CMD programaker-gitlab-service
