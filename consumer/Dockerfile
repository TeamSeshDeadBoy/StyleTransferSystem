# syntax = docker/dockerfile:1.5
# FROM python:3.9-alpine3.13
FROM base_python/1
# RUN apk add bash
COPY . /app
WORKDIR /app
# RUN --mount=type=cache,target=/root/.cache \
#     pip install -r requirements.txt
RUN bash check.sh
ENTRYPOINT ["bash", "run.sh"]