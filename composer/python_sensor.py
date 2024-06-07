from airflow import DAG
from airflow.operators.python import BranchPythonOperator, PythonOperator
from airflow.sensors.python import PythonSensor
from airflow.operators.dummy import DummyOperator
from airflow.utils.dates import days_ago
from datetime import datetime
import holidays

def is_business_day_func():
    today = datetime.now().date()
    us_holidays = holidays.US()
    return today.weekday() < 5 and today not in us_holidays

def is_business_day(**kwargs):
    if is_business_day_func():
        return 'check_data_sensor'
    return 'not_a_business_day'

def check_data_func():
    # Replace with your actual data check logic
    return True  # Simulating that the condition is met

def send_email(**kwargs):
    # Placeholder function for sending an email
    print("Sending email...")

default_args = {
    'start_date': days_ago(1),
    'retries': 1,
}

with DAG(
    'simple_python_sensor_dag_with_checks',
    default_args=default_args,
    description='A simple DAG with business day check and PythonSensor',
    schedule_interval=None,
) as dag:

    start = DummyOperator(task_id='start')

    check_business_day = BranchPythonOperator(
        task_id='check_business_day',
        python_callable=is_business_day,
        provide_context=True,
    )

    not_a_business_day = DummyOperator(task_id='not_a_business_day')

    check_data_sensor = PythonSensor(
        task_id='check_data_sensor',
        python_callable=check_data_func,
        mode='poke',
        poke_interval=300,  # Check every 5 minutes
        timeout=60 * 60 * 24,  # Timeout after 24 hours
    )

    send_email_task = PythonOperator(
        task_id='send_email',
        python_callable=send_email,
        provide_context=True,
    )

    end = DummyOperator(task_id='end')

    start >> check_business_day
    check_business_day >> not_a_business_day >> end
    check_business_day >> check_data_sensor >> send_email_task >> end
