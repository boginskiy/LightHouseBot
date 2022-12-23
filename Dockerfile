FROM python:3.10-slim

RUN mkdir /app
COPY . /app
RUN pip3 install -r /app/requirements.txt --no-cache-dir

ENV BOT_TOKEN '5872260590:AAFAfXYX84VM4x-ze2LrSWiMXB9Oi84ELPQ'
ENV ID_ADMIN 5339878954

WORKDIR /app
CMD ["python3", "lighthouse.py"]
