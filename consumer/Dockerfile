# syntax = docker/dockerfile:1.5
FROM base_python/1
COPY . /app
WORKDIR /app
RUN --mount=type=cache,target=/root/.cache \
    pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
RUN --mount=type=cache,target=/root/.cache \
    pip install -r requirements.txt
RUN bash check.sh
ENTRYPOINT ["bash", "run.sh"]