FROM python:3.11 AS requirements_stage

WORKDIR /wheel

RUN python -m pip install --user pipx pdm

COPY ./pyproject.toml ./pdm.lock /wheel/

RUN python -m pipx run --no-cache nb-cli generate -f /tmp/bot.py
RUN python -m pdm export -o /tmp/requirements.txt


FROM python:3.11-slim

WORKDIR /app

ENV TZ=Asia/Shanghai \
    PYTHONPATH=/app

COPY ./docker/gunicorn_conf.py ./docker/start.sh /

RUN chmod +x /start.sh

ENV APP_MODULE=_main:app \
    MAX_WORKERS=1

COPY --from=requirements_stage /tmp/requirements.txt /app
COPY --from=requirements_stage /tmp/bot.py /app

RUN pip install --no-cache-dir gunicorn uvicorn[standard]
RUN pip install --no-cache-dir -r ./requirements.txt

RUN rm -rf ./requirements.txt

COPY ./docker/_main.py /app
COPY . /app/

CMD ["/start.sh"]
