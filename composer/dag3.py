from airflow import DAG
from airflow.operators.python import BranchPythonOperator, PythonOperator
from airflow.operators.dummy import DummyOperator
from airflow.sensors.time_delta import TimeDeltaSensor
from airflow.utils.dates import days_ago
from datetime import datetime, timedelta
from google.cloud import bigquery
import holidays

def is_business_day(**kwargs):
    today = datetime.now().date()
    us_holidays = holidays.US()
    if today.weekday() < 5 and today not in us_holidays:
        return 'check_data_in_table_1'
    return 'not_a_business_day'

def check_data_in_table_1(**kwargs):
    client = bigquery.Client()
    query = "SELECT COUNT(1) FROM `your_project.your_dataset.table_1` WHERE <your_condition>"
    query_job = client.query(query)
    results = query_job.result()
    for row in results:
        if row[0] > 0:
            return 'send_email'
    return 'retry_check_table_1'

def send_email(**kwargs):
    # Placeholder function for sending an email
    print("Sending email...")

default_args = {
    'start_date': days_ago(1),
    'retries': 1,
}

with DAG(
    'simple_check_dag',
    default_args=default_args,
    description='A DAG with simple checks and retries',
    schedule_interval=None,
) as dag:

    start = DummyOperator(task_id='start')

    check_business_day = BranchPythonOperator(
        task_id='check_business_day',
        python_callable=is_business_day,
        provide_context=True,
    )

    not_a_business_day = DummyOperator(task_id='not_a_business_day')

    check_data_in_table_1 = BranchPythonOperator(
        task_id='check_data_in_table_1',
        python_callable=check_data_in_table_1,
        provide_context=True,
    )

    retry_check_table_1 = TimeDeltaSensor(
        task_id='retry_check_table_1',
        delta=timedelta(minutes=5),
    )

    retry_check_table_1_step = DummyOperator(task_id='retry_check_table_1_step')

    send_email_task = PythonOperator(
        task_id='send_email',
        python_callable=send_email,
        provide_context=True,
    )

    end = DummyOperator(task_id='end')

    start >> check_business_day
    check_business_day >> check_data_in_table_1
    check_business_day >> not_a_business_day >> end
    check_data_in_table_1 >> send_email_task >> end
    check_data_in_table_1 >> retry_check_table_1_step >> retry_check_table_1
    retry_check_table_1 >> check_data_in_table_1
