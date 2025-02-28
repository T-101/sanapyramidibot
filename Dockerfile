FROM python:3.13.1-alpine
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apk add --no-cache tzdata
ENV TZ=Europe/Helsinki

COPY requirements.txt /app

RUN pip install -r requirements.txt

COPY . /app

CMD ["python", "bot.py"]