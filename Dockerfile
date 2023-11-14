FROM python:3.10-slim-bullseye

LABEL maintainer="jingfelix@outlook.com"

EXPOSE 5050

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install pip requirements
COPY requirements.txt .
RUN python -m pip install --no-cache-dir --upgrade -r requirements.txt
# RUN python -m pip install --no-cache-dir --upgrade -r requirements.txt -i https://mirrors.hust.edu.cn/pypi/web/simple
RUN python -m spacy download zh_core_web_sm

WORKDIR /app
VOLUME /app
COPY ./server /app/server
COPY ./main.py ./gunicorn.conf.py /app

RUN mkdir -p /app/index_ix && mkdir -p /app/instance && mkdir -p /app/log

CMD ["/usr/local/bin/gunicorn", "-c", "/app/gunicorn.conf.py", "main:app"]