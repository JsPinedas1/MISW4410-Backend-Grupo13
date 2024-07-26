FROM python:3.9

RUN apt-get update && apt-get install -y wget \
    && wget -O dockerize.tar.gz https://github.com/jwilder/dockerize/releases/download/v0.6.1/dockerize-linux-amd64-v0.6.1.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize.tar.gz \
    && rm dockerize.tar.gz \
    && chmod +x /usr/local/bin/dockerize

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

CMD ["dockerize", "-wait", "tcp://db:5432", "-timeout", "30s", "python", "app.py"]
