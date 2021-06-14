FROM python:slim

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY  ./elasticsearch-private-geoip.py ./

CMD [ "python", "./elasticsearch-private-geoip.py" ]