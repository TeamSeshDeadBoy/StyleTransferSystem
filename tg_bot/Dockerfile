FROM base_python:1
# RUN apk update && apk add bash
COPY . /app
WORKDIR /app
# RUN --mount=type=cache,target=/root/.cache \
#     pip install -r requirements.txt
ENTRYPOINT [ "python3", "src/main.py" ]