from airflow import DAG # type: ignore
from airflow.operators.python_operator import PythonOperator # type: ignore
from datetime import datetime, timedelta
from access_twitch_api import getTop50
from data_manager import save_in_database

def salvar_dados(**context):
    execution_date = context['execution_date']
    save_in_database(execution_date)

with DAG(
    "extrair_dados_twitch",
    default_args={
        'start_date':datetime(2025, 5, 7),
        'retries':1,
        'retry_delay':timedelta(minutes=2),
    },
    schedule_interval = '*/10 * * * *',
    catchup=False
) as dag:
    
    taskExtract = PythonOperator(
        task_id='extrair_dados',
        python_callable=getTop50
    )

    taskSave = PythonOperator(
        task_id='salvar_dados',
        python_callable=salvar_dados,
        provide_context=True
    )

    taskExtract >> taskSave