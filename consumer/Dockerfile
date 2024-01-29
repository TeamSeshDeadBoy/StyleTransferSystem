FROM python:3.9-alpine3.13
RUN apk update && apk add bash
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
ENTRYPOINT ["bash", "run.sh"]