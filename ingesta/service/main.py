import boto3
import os
import json
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_SESSION_TOKEN = os.getenv("AWS_SESSION_TOKEN")
DYNAMODB_TABLES = os.getenv("DYNAMODB_TABLES")
S3_BUCKET = os.getenv("S3_BUCKET")
STAGE = os.getenv("STAGE")
CONTAINER_NAME = os.getenv("CONTAINER_NAME")

tables = [table.strip() + '-' + STAGE for table in DYNAMODB_TABLES.split(",")]

log_directory = "/logs"
os.makedirs(log_directory, exist_ok=True)

log_file = os.path.join(log_directory, f"{CONTAINER_NAME}.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file, mode="a", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger()

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

def scan_dynamodb(table_name):
    paginator = dynamodb.get_paginator('scan')
    for page in paginator.paginate(TableName=table_name):
        yield from page.get('Items', [])

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
    return {key: extract_value(value) for key, value in item.items()}

def save_to_json_lines(data, file_name):
    try:
        transformed_data = [transform_dynamodb_item(item) for item in data]
        with open(file_name, mode='w', encoding='utf-8') as file:
            for record in transformed_data:
                file.write(json.dumps(record, ensure_ascii=False) + '\n')
        logger.info(f"Archivo JSON Lines guardado: {file_name} con {len(data)} registros.")
    except Exception as e:
        logger.error(f"Error al guardar archivo JSON Lines: {e}")
        raise

def upload_to_s3(file_name, bucket, s3_key):
    try:
        s3.upload_file(file_name, bucket, s3_key)
        logger.info(f"Archivo subido exitosamente a S3: {s3_key}")
    except Exception as e:
        logger.error(f"Error al subir el archivo a S3: {e}")
        raise

if __name__ == "__main__":
    start_time = datetime.now()
    logger.info(f"Inicio del proceso de ingesta - Contenedor: {CONTAINER_NAME}")
    try:
        for table in tables:
            table_start_time = datetime.now()
            logger.info(f"Procesando tabla DynamoDB: {table} - Inicio: {table_start_time}")
            try:
                data = list(scan_dynamodb(table))
                logger.info(f"Tabla {table} escaneada. Registros encontrados: {len(data)}")

                file_name = f"{table}_data.json"
                save_to_json_lines(data, file_name)

                folder_name = table.replace('-', '_')
                s3_key = f"{folder_name}/{file_name}"
                upload_to_s3(file_name, S3_BUCKET + "-" + STAGE, s3_key)

            except Exception as table_error:
                logger.error(f"Error procesando tabla {table}: {table_error}")

            finally:
                table_end_time = datetime.now()
                logger.info(f"Finalización de tabla {table}. Duración: {table_end_time - table_start_time}")
    except Exception as e:
        logger.error(f"Error durante el proceso general: {e}")
    finally:
        process_end_time = datetime.now()
        logger.info(f"Proceso completado. Inicio: {start_time}, Fin: {process_end_time}, Duración total: {process_end_time - start_time}")
