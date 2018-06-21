FROM python:3.6

RUN pip install pipenv

COPY /Pipfile /Pipfile
COPY /Pipfile.lock /Pipfile.lock

RUN pipenv install --system

COPY /telegram_bot /telegram_bot

WORKDIR /

CMD ["python", "-m", "telegram_bot"]
