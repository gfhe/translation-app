FROM hgfkeep/translation:base
COPY src /app
RUN mkdir /app/logs
WORKDIR /app
EXPOSE 7000
ENV TRANSFORMERS_OFFLINE=1
ENV HUGGINGFACE_HUB_CACHE=/root/.cache/huggingface/hub
CMD gunicorn -c gunicorn_config.py translation:apps
#RUN python translation.py