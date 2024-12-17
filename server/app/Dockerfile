FROM python:3.11

WORKDIR /app

# Вставка зависимостей и запуск их обновлений до копирования всей директории запустит продвинутую систему кэшировния
# docker, что поможет избежать повторной установки зависимостей
COPY requirements.txt .

RUN python -m pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install gunicorn

COPY . /app

EXPOSE 5000
