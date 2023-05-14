FROM python:3.10

WORKDIR /fastapi_app

COPY ./requirements.txt /fastapi_app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /fastapi_app/requirements.txt

COPY . /fastapi_app

RUN chmod +x ./docker/*.sh

ENTRYPOINT ["./docker/app.sh"]

ENV PYTHONPATH "${PYTHONPATH}:/fastapi_app/"