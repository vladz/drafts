FROM python:3

RUN apt-get update && apt-get install --no-install-recommends -y \
    uwsgi-core uwsgi-plugin-python3
RUN python3.6 -m pip install pipenv

COPY /Pipfile /Pipfile
COPY /Pipfile.lock /Pipfile.lock

RUN pipenv install --system

COPY /docker-entrypoint.sh /
COPY /ga /ga

WORKDIR /

CMD ["uwsgi", "--ini", "/ga/uwsgi.ini"]
