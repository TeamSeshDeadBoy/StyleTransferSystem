FROM python:3.9-alpine3.13
RUN apk update && apk add bash
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
ENTRYPOINT [ "python3", "src/main.py" ]