from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from azure.storage.blob import BlobServiceClient
import pandas as pd
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()
AZURE_CONNECTION_STRING = os.getenv("AZURE_CONNECTION_STRING")
AZURE_CONTAINER_NAME = 'csvfile'
LOCAL_CSV_FILE = "/opt/airflow/data/test.csv"

def export_csv_to_azure_blob():
    with open(LOCAL_CSV_FILE, 'rb') as file:
        blob_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
        print("Uploading...")
        blob_name = f"exported_file_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
        blob_container = blob_client.get_container_client(AZURE_CONTAINER_NAME)
        blob_container.upload_blob(blob_name, file, overwrite=True)
        print(f"File {blob_name} is uploaded")


with DAG(
    dag_id='export_csv_to_azure_blob',
    schedule='@daily',
    start_date=datetime(2024, 4, 29),
    catchup=False,
    default_args={
        "retries": 1
    },
    description='test export local file to azure storage',
    default_view="graph"
) as dag:
    begin = EmptyOperator(task_id="begin")
    end = EmptyOperator(task_id='end')
    export_task = PythonOperator(
        task_id='export_csv',
        python_callable=export_csv_to_azure_blob
    )

# Définir les dépendances
begin >> export_task >> end