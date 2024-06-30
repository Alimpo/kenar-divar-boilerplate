FROM python:3.12-bullseye

WORKDIR /app

COPY requirements.txt ./

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["/bin/sh", "run.sh"]
