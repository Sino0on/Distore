FROM nginx

RUN rm /etc/nginx/conf.d/default.conf

ARG NGINX_FILE_PATH
COPY ${NGINX_FILE_PATH} etc/nginx/conf.d