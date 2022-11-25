FROM hgfkeep/translation:base
COPY src /app
RUN mkdir /app/logs
WORKDIR /app
EXPOSE 7000
CMD gunicorn -c gunicorn_config.py translation:apps
#RUN python translation.py