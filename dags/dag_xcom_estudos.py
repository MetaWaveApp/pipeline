from airflow import DAG # type: ignore 
from airflow.operators.python_operator import PythonOperator # type: ignore 
from datetime import datetime, timedelta
import logging

def taksFuncTipo1(**kwargs):
    ti = kwargs['ti']
    ti.xcom_push(key='message', value="teste")

def consumeMessage(**kwargs):
    ti = kwargs['ti']
    logging.info('t2 - consumiu a mensagem:')
    logging.info(ti.xcom_pull(key='message'))

def consumeMessaget3(**kwargs):
    ti = kwargs['ti']
    logging.info('t3 - consumiu a mensagem:')
    logging.info(ti.xcom_pull(key='message'))

with DAG(
    "dag_xcom_estudos",
    default_args={
        'start_date':datetime(2025, 5, 7),
        'retries':1,
        'retry_delay':timedelta(minutes=2),
    },
    schedule_interval = '*/10 * * * *',
    catchup=False
) as dag:
    
    t1 = PythonOperator (
        task_id='t1',
        python_callable=taksFuncTipo1,
        provide_context= True
    )

    t2 = PythonOperator (
        task_id='t2',
        python_callable=consumeMessage,
        provide_context= True
    )

    t3 = PythonOperator (
        task_id='t3',
        python_callable=consumeMessaget3,
        provide_context= True
    )

    t1 >> [t2, t3]