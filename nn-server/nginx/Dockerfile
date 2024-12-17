FROM nginx:latest

# Устанавливаем netcat-openbsd
RUN apt-get update && apt-get install -y netcat-openbsd

# Устанавливаем конфигурацию nginx
RUN rm -f /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d

# Копируем .htpasswd
COPY .htpasswd /etc/nginx/.htpasswd

# Добавляем скрипт ожидания приложения
COPY wait-for-it.sh /usr/bin/wait-for-it.sh
RUN chmod +x /usr/bin/wait-for-it.sh

RUN mkdir -p /home/web/default

# Запуск NGINX через скрипт wait-for-it.sh
CMD ["/bin/bash", "-c", "/usr/bin/wait-for-it.sh nn-server 5001 -- nginx -g 'daemon off;'"]
