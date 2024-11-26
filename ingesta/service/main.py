import boto3
import os
import json
from dotenv import load_dotenv

load_dotenv()

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
    transformed = {}
    for key, value in item.items():
        transformed[key] = extract_value(value)
    return transformed

def save_to_json_lines(data, file_name):
    transformed_data = [transform_dynamodb_item(item) for item in data]
    with open(file_name, mode='w', encoding='utf-8') as file:
        for record in transformed_data:
            file.write(json.dumps(record, ensure_ascii=False) + '\n')
    print(f"Archivo JSON Lines guardado: {file_name}")

def upload_to_s3(file_name, bucket, s3_key):
    try:
        s3.upload_file(file_name, bucket, s3_key)
        print(f"Archivo subido exitosamente a S3: {s3_key}")
    except Exception as e:
        print(f"Error al subir el archivo a S3: {e}")

if __name__ == "__main__":
    for table in tables:
        print(f"Procesando tabla DynamoDB: {table}")
        data = list(scan_dynamodb(table))
        file_name = f"{table}_data.json"
        save_to_json_lines(data, file_name)

        folder_name = table.replace('-', '_')
        s3_key = f"{folder_name}/{file_name}"
        upload_to_s3(file_name, S3_BUCKET + "-" + STAGE, s3_key)
