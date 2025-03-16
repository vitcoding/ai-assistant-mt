FROM python:3.11 AS base

WORKDIR /opt/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update \
    && apt-get install -y --no-install-recommends netcat-openbsd ffmpeg espeak-ng

FROM base AS dependencies

COPY src/requirements.txt .

RUN pip install --upgrade --no-cache-dir pip \
    && pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

COPY src/entrypoint.sh /
RUN chmod +x /entrypoint.sh

COPY src .

ENTRYPOINT ["/entrypoint.sh"]