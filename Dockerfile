FROM hgfkeep/translation:base
LABEL maintainer="HGF"
LABEL repository="hgfkeep"

COPY src /app
RUN mkdir /app/logs
WORKDIR /app
EXPOSE 7000
ENV TRANSFORMERS_OFFLINE=1
CMD gunicorn -c gunicorn_config.py translation:apps
#RUN python translation.py