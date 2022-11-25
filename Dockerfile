FROM python:3.9
COPY src /app
RUN pip install -r /app/requirements.txt -f https://download.pytorch.org/whl/torch_stable.html
COPY init.py /init.py
RUN python /init.py && rm /init.py
WORKDIR /app