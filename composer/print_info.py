import pkg_resources
import inspect
from airflow.providers.google.cloud.hooks.compute_ssh import ComputeEngineSSHHook
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime


def print_provider_info():
    # Print the version of airflow-provider-google
    google_provider_version = pkg_resources.get_distribution("apache-airflow-providers-google").version
    print("Apache Airflow Google Provider Version:", google_provider_version)
    
    # Optionally, print the source code of ComputeEngineSSHHook (you can limit the number of lines if it's too long)
    source = inspect.getsource(ComputeEngineSSHHook)
    print("Source Code for ComputeEngineSSHHook:\n", source[:1000])  # printing first 1000 characters



default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': datetime.timedelta(minutes=5),
}

with DAG(
    'google_provider_info_dag',
    default_args=default_args,
    description='A print Google provider version and inspect ComputeEngineSSHHook code',
    schedule_interval=datetime.timedelta(days=1),
    start_date=datetime(2024, 4, 26),
    catchup=False
) as dag:

    print_info = PythonOperator(
        task_id='print_provider_info',
        python_callable=print_provider_info
    )

    print_info
