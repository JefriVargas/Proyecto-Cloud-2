FROM python:3.9-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

EXPOSE 3306

CMD ["python", "main.py"]
