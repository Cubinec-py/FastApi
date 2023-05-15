FROM python:3.10

WORKDIR /fastapi_app

ENV PYTHONPATH "${PYTHONPATH}:/fastapi_app/"

COPY ./requirements.txt /fastapi_app/requirements.txt

RUN pip install -U pip && pip install --no-cache-dir --upgrade -r /fastapi_app/requirements.txt

COPY . /fastapi_app

RUN chmod +x /fastapi_app/docker/*.sh

ENTRYPOINT ["/fastapi_app/docker/app.sh"]