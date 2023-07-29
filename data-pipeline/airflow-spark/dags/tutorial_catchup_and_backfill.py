from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator


default_args = {
    'owner': 'airflow',
    'retries': 5,
    'retry_delay': timedelta(minutes=5)
}

with DAG(
    dag_id='tutorial_catchup_backfill',
    default_args=default_args,
    start_date=datetime(2023, 7, 5),
    schedule='@daily',
    catchup=False
) as dag:
    """
    1. catchup = False -> only run latest -> need use backfill to run all in the pass:
    $ airflow dags backfill -s 2023-07-05 -e 2023-07-10 tutorial_catchup_backfill
    
    2. catchup = True -> run all in the pass
    """
    task1 = BashOperator(
        task_id='task1',
        bash_command='echo This is a simple bash command!'
    )