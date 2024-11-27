import boto3
import os
import pymysql
from datetime import datetime
from dotenv import load_dotenv
from querys import Queries
from models import (
    Ordenes,
    Horarios,
    Peliculas,
    Productos,
    Reservas,
    Usuarios,
    OrdenesProductos
)
import json
from transform import Transform
import logging

load_dotenv()

log_dir = "/logs"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "etl_process.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ETL Process")

AWS_REGION = os.getenv("AWS_REGION")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_SESSION_TOKEN = os.getenv("AWS_SESSION_TOKEN")

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")
MYSQL_PORT = os.getenv("MYSQL_PORT")

athena = boto3.client(
    "athena",
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    aws_session_token=AWS_SESSION_TOKEN,
)

def execute_athena_query(query, output_location):
    try:
        response = athena.start_query_execution(
            QueryString=query,
            QueryExecutionContext={"Database": "catalogo_dev"},
            ResultConfiguration={"OutputLocation": output_location},
        )
        query_id = response["QueryExecutionId"]
        logger.info(f"Consulta iniciada con ID: {query_id}")
        return query_id
    except Exception as e:
        logger.error(f"Error ejecutando la consulta en Athena: {e}")
        raise

def get_query_results(query_execution_id):
    try:
        while True:
            response = athena.get_query_execution(QueryExecutionId=query_execution_id)
            state = response["QueryExecution"]["Status"]["State"]
            if state in ["SUCCEEDED", "FAILED", "CANCELLED"]:
                if state != "SUCCEEDED":
                    logger.error(f"Consulta fallida en Athena. Estado: {state}")
                    raise Exception(f"Consulta fallida en Athena: {state}")
                logger.info(f"Consulta con ID {query_execution_id} finalizó con estado: {state}")
                break
        rows = athena.get_query_results(QueryExecutionId=query_execution_id)["ResultSet"]["Rows"]
        logger.info(f"Consulta con ID {query_execution_id} retornó {len(rows) - 1} registros.")
        return rows
    except Exception as e:
        logger.error(f"Error obteniendo resultados de Athena: {e}")
        raise

def transform_athena_result(data_rows):
    headers = [col.get("VarCharValue") for col in data_rows[0].get("Data", [])]
    results = []
    for row in data_rows[1:]:
        values = [col.get("VarCharValue", None) for col in row.get("Data", [])]
        row_dict = dict(zip(headers, values))
        if "products" in row_dict and row_dict["products"]:
            try:
                row_dict["products"] = json.loads(row_dict["products"])
            except json.JSONDecodeError:
                row_dict["products"] = None
        results.append(row_dict)
    logger.info(f"Transformación completada para {len(results)} registros.")
    return results

def map_to_schema(data: list[dict], schema):
    validated_data = []
    for record in data:
        try:
            validated_data.append(schema(**record))
        except Exception as e:
            logger.warning(f"Error validando registro: {record}, Error: {e}")
    logger.info(f"{len(validated_data)} registros validados exitosamente contra el esquema {schema.__name__}.")
    return validated_data

def load_to_mysql(data, table_name):
    try:
        connection = pymysql.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE,
            port=int(MYSQL_PORT)
        )
        with connection.cursor() as cursor:
            for record in data:
                columns = ", ".join(record.keys())
                placeholders = ", ".join(["%s"] * len(record))
                sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
                cursor.execute(sql, list(record.values()))
        connection.commit()
        logger.info(f"{len(data)} registros cargados en la tabla {table_name}.")
    except Exception as e:
        logger.error(f"Error cargando datos en MySQL: {e}")
        raise
    finally:
        connection.close()

if __name__ == "__main__":
    start_time = datetime.now()
    output_location = "s3://logs123123213/"

    queries = [
        ("usuarios", Queries.usuarios_query(), "Usuarios", Transform(
            primary_schema=Usuarios,
            related_schema=None,
            relation_field=None
        )),
        ("productos", Queries.productos_query(), "Productos", Transform(
            primary_schema=Productos,
            related_schema=None,
            relation_field=None
        )),
        ("peliculas", Queries.peliculas_query(), "Peliculas", Transform(
            primary_schema=Peliculas,
            related_schema=None,
            relation_field=None
        )),
        ("horarios", Queries.horarios_query(), "Horarios", Transform(
            primary_schema=Horarios,
            related_schema=None,
            relation_field=None
        )),
        ("reservas", Queries.reservas_query(), "Reservas", Transform(
            primary_schema=Reservas,
            related_schema=None,
            relation_field=None
        )),
        ("ordenes", Queries.ordenes_query(), "Ordenes", Transform(
            primary_schema=Ordenes,
            related_schema=OrdenesProductos,
            relation_field="products"
        )),
    ]

    for name, query, table, transformer in queries:
        process_start_time = datetime.now()
        logger.info(f"Procesando {name} - Hora de inicio: {process_start_time}")
        try:
            query_id = execute_athena_query(query, output_location)
            results = get_query_results(query_id)

            data = transform_athena_result(results)
            transformed_data = transformer.transform(data)

            logger.info(f"Cargando datos principales en MySQL para la tabla {table}...")
            load_to_mysql(transformed_data["primary"], table)

            if transformed_data.get("related"):
                related_table = f"{table}_related" if name != "ordenes" else "OrdenesProductos"
                logger.info(f"Cargando datos relacionados en MySQL para la tabla {related_table}...")
                load_to_mysql(transformed_data["related"], related_table)

        except Exception as e:
            logger.error(f"Error procesando {name}: {e}")
        finally:
            process_end_time = datetime.now()
            logger.info(f"Finalizado {name} - Hora de fin: {process_end_time} - Duración: {process_end_time - process_start_time}")

    end_time = datetime.now()
    logger.info(f"ETL finalizado. Hora de inicio: {start_time}, Hora de fin: {end_time}, Duración total: {end_time - start_time}")
