from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from airflow.models import TaskInstance
from airflow import settings
from datetime import datetime, timedelta
import pytz

def clear_task_instances_func(dag_id: str, start_date: datetime, end_date: datetime = None):
    session = settings.Session()
    
    # Query for the task instances within the date range
    query = session.query(TaskInstance).filter(
        TaskInstance.dag_id == dag_id,
        TaskInstance.execution_date >= start_date
    )
    
    if end_date:
        query = query.filter(TaskInstance.execution_date <= end_date)
    
    tis = query.all()

    # Set the state of the task instances to None (cleared)
    for ti in tis:
        ti.state = None
    session.commit()
    session.close()

# Define the timezone
eastern = pytz.timezone("US/Eastern")

# Define the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'clear_task_instances_dag',
    default_args=default_args,
    description='A DAG to clear task instances',
    schedule_interval=None,  # Manual trigger only
    start_date=days_ago(1),
    catchup=False,
) as dag:

    # Define the task
    clear_task = PythonOperator(
        task_id='clear_task_instances_task',
        python_callable=clear_task_instances_func,
        op_kwargs={
            'dag_id': 'DEPOSITS_RUNNER_NEW',
            'start_date': eastern.localize(datetime(2024, 6, 10, 0, 0, 0)),
            'end_date': eastern.localize(datetime(2024, 6, 12, 0, 0, 0))  # You can adjust the end date as needed
        },
    )

    clear_task
