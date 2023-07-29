from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.utils.dates import days_ago
from datetime import timedelta


args = {
    'owner': 'Airflow',
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='tutorial_spark_submit_operator',
    default_args=args,
    schedule='@daily',
    start_date=days_ago(2),
) as dag:

    start = EmptyOperator(task_id="start", dag=dag)

    spark_job = SparkSubmitOperator(
        application="/opt/spark/app/hello-world-spark.py",
        conn_id="spark_default",
        task_id="spark_submit_task",
        application_args=["/opt/spark/resources/data/test.csv"],
        dag=dag
    )

    end = EmptyOperator(task_id="end", dag=dag)

    start >> spark_job >> end
    