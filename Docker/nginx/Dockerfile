FROM nginx:1.19
COPY nginx.conf /etc/nginx/
RUN chown -R www-data:www-data /etc/nginx && chown -R www-data:www-data /tmp \
    && chown -R www-data:www-data /usr/share/nginx && chown -R www-data:www-data /var/cache/nginx \
    && chown -R www-data:www-data /var/log/nginx
USER www-data
