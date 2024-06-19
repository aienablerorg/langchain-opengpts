# Backend Dockerfile
FROM python:3.11

# Install system dependencies
RUN apt-get update && apt-get install -y libmagic1 vim \
    && rm -rf /var/lib/apt/lists/* \
    && curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" \
    && install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Set the working directory
WORKDIR /backend

COPY ./backend .

RUN rm poetry.lock
# RUN pip install poetry

# RUN poetry install

# RUN --mount=type=cache,target=/root/.cache \
#     pip install .

RUN pip install .

CMD exec uvicorn app.server:app --host 0.0.0.0 --port $PORT