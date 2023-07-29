from airflow import DAG
from docker.types import Mount
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.operators.python import BranchPythonOperator
from airflow.operators.empty import EmptyOperator
import os


default_args = {
    'owner': 'airflow',
    'description': 'Use of the DockerOperator',
    'depend_on_past': False,
    'start_date': datetime(2023, 1, 3),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def check_repo():
    if os.path.exists('/home/airflow/simple-app/.git'):
        return 'dummy'
    return 'git_clone'

with DAG(
    'tutorial_docker_simple_spark',
    default_args=default_args,
    schedule="@daily",
    catchup=False
) as dag:

    t_check_repo = BranchPythonOperator(
        task_id='is_repo_exists',
        python_callable=check_repo
    )

    t_git_clone = BashOperator(
        task_id='git_clone',
        bash_command='git clone https://github.com/marclamberti/simple-app.git /home/airflow/simple-app'
    )

    t_git_pull = BashOperator(
        task_id='git_pull',
        bash_command='cd /home/airflow/simple-app && git pull',
        trigger_rule='one_success'
    )

    # Notice the trigger_rule sets to one_success
    # Why?
    # By default your tasks are set to all_success, so all parents must succeed for the task to be triggered
    # Here t_git_pull depends on either t_git_clone or t_dummy
    # By default if one these tasks is skipped then its downstream tasks will be skipped as well since the trigger_rule is set to all_succeed and so invalidate the task.
    # With one_success, t_git_pull will not be skipped since it now needs only either dummy or git_clone to succeed.

    t_dummy = EmptyOperator(task_id='dummy')

    t_docker = DockerOperator(
        task_id='docker_command',
        image='bde2020/spark-master:latest',
        api_version='auto',
        auto_remove=True,
        environment={
            'PYSPARK_PYTHON': "python3",
            'SPARK_HOME': "/spark"
        },
        mounts=[
            Mount(
                source="/home/hoang/Documents/datamining/airflow-spark/simple-app",
                target="/simple-app",
                type="bind"
            )
        ],
        command='/spark/bin/spark-submit --master local[*] /simple-app/SimpleApp.py',
        docker_url='unix://var/run/docker.sock',
        network_mode='bridge'
    )

    t_check_repo >> [t_git_clone, t_dummy] >> t_git_pull >> t_docker
