FROM python:3.8

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update \
    && apt-get dist-upgrade -y \
    && apt-get install netcat postgresql gcc python3-dev musl-dev -y

WORKDIR /app/drf_book

RUN pip install --upgrade pip
COPY ./reqs.txt /app
RUN pip install -r /app/reqs.txt

COPY . .

EXPOSE 8000

RUN chmod +x /app/drf_book/entrypoint.sh
ENTRYPOINT ["bash","/app/drf_book/entrypoint.sh"]
