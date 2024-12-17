FROM nginx:latest

# Устанавливаем netcat-openbsd
RUN apt-get update && apt-get install -y netcat-openbsd

RUN mkdir -p /home/web/default

# Устанавливаем конфигурацию nginx
RUN rm -f /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d

# Настройка прав доступа к сертификатам
ARG CERTS_FOLDER
COPY certs/${CERTS_FOLDER} /home/web/default/certs
RUN chmod 644 /home/web/default/certs/*

# Копируем папку для проверки сертификата
COPY .well-known /home/web/default/.well-known

# Добавляем скрипт ожидания приложения
COPY wait-for-it.sh /usr/bin/wait-for-it.sh
RUN chmod +x /usr/bin/wait-for-it.sh

# Запуск NGINX через скрипт wait-for-it.sh
CMD ["/bin/bash", "-c", "/usr/bin/wait-for-it.sh web-server 5000 -- nginx -g 'daemon off;'"]
