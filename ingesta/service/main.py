import boto3
import os
import json
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

container_name = os.getenv("CONTAINER_NAME")
log_directory = "/home/ubuntu/Proyecto-Cloud-2/logs"
os.makedirs(log_directory, exist_ok=True)
log_file = os.path.join(log_directory, f"{container_name}.log")

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s]: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S.%f"
)
logger = logging.getLogger(container_name)

AWS_REGION = os.getenv("AWS_REGION")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_SESSION_TOKEN = os.getenv("AWS_SESSION_TOKEN")
DYNAMODB_TABLES = os.getenv("DYNAMODB_TABLES")
S3_BUCKET = os.getenv("S3_BUCKET")
STAGE = os.getenv("STAGE")

tables = [table.strip() + '-' + STAGE for table in DYNAMODB_TABLES.split(",")]

dynamodb = boto3.client(
    'dynamodb',
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    aws_session_token=AWS_SESSION_TOKEN
)

s3 = boto3.client(
    's3',
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    aws_session_token=AWS_SESSION_TOKEN
)

def log_event(level, message):
    if level == "INFO":
        logger.info(message)
    elif level == "WARNING":
        logger.warning(message)
    elif level == "ERROR":
        logger.error(message)
    elif level == "CRITICAL":
        logger.critical(message)

def scan_dynamodb(table_name):
    paginator = dynamodb.get_paginator('scan')
    try:
        for page in paginator.paginate(TableName=table_name):
            yield from page.get('Items', [])
        log_event("INFO", f"Scan exitoso en la tabla {table_name}.")
    except Exception as e:
        log_event("ERROR", f"Error al escanear la tabla {table_name}: {e}")

def extract_value(value):
    for dtype, dvalue in value.items():
        if dtype == 'S':
            return dvalue
        elif dtype == 'N':
            return int(dvalue) if '.' not in dvalue else float(dvalue)
        elif dtype == 'BOOL':
            return dvalue
        elif dtype == 'NULL':
            return None
        elif dtype == 'M':
            return {k: extract_value(v) for k, v in dvalue.items()}
        elif dtype == 'L':
            return [extract_value(i) for i in dvalue]
    return value

def transform_dynamodb_item(item):
    transformed = {}
    for key, value in item.items():
        transformed[key] = extract_value(value)
    return transformed

def save_to_json_lines(data, file_name):
    transformed_data = [transform_dynamodb_item(item) for item in data]
    try:
        with open(file_name, mode='w', encoding='utf-8') as file:
            for record in transformed_data:
                file.write(json.dumps(record, ensure_ascii=False) + '\n')
        log_event("INFO", f"Archivo JSON Lines guardado: {file_name}")
    except Exception as e:
        log_event("ERROR", f"Error al guardar el archivo JSON Lines: {e}")

def upload_to_s3(file_name, bucket, s3_key):
    try:
        s3.upload_file(file_name, bucket, s3_key)
        log_event("INFO", f"Archivo subido exitosamente a S3: {s3_key}")
    except Exception as e:
        log_event("ERROR", f"Error al subir el archivo a S3: {e}")

if __name__ == "__main__":
    start_time = datetime.now()
    log_event("INFO", "Inicio del proceso de ingesta.")

    try:
        for table in tables:
            log_event("INFO", f"Procesando tabla DynamoDB: {table}")
            data = list(scan_dynamodb(table))
            file_name = f"{table}_data.json"
            save_to_json_lines(data, file_name)

            folder_name = table.replace('-', '_')
            s3_key = f"{folder_name}/{file_name}"
            upload_to_s3(file_name, S3_BUCKET + "-" + STAGE, s3_key)

        log_event("INFO", "Proceso de ingesta completado exitosamente.")
    except Exception as e:
        log_event("CRITICAL", f"Error crítico en el proceso de ingesta: {e}")

    end_time = datetime.now()
    duration = end_time - start_time
    log_event("INFO", f"Duración del proceso: {duration}")
