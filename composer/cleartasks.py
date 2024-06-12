from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from airflow.api.common.experimental.mark_tasks import clear_task_instances
from airflow.models import TaskInstance
from airflow import settings

# Function to clear task instances
def clear_task_instances_func():
    dag_id = 'daily_8am_et_reset'
    session = settings.Session()

    # Clear all task instances for this DAG
    tis = session.query(TaskInstance).filter(TaskInstance.dag_id == dag_id).all()
    clear_task_instances(tis, session)
    session.commit()

# Define the DAG
with DAG(
    'clear_task_instances_dag',
    default_args={
        'owner': 'airflow',
        'depends_on_past': False,
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
    },
    description='A DAG to clear task instances',
    schedule_interval=None,  # Manual trigger only
    start_date=days_ago(1),
    catchup=False,
) as dag:

    # Define the task
    clear_task = PythonOperator(
        task_id='clear_task_instances_task',
        python_callable=clear_task_instances_func,
    )

    clear_task
