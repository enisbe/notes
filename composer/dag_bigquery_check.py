from datetime import timedelta
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from airflow.providers.google.cloud.operators.dataproc import DataprocSubmitJobOperator
from airflow.providers.google.cloud.sensors.dataproc import DataprocJobSensor
from airflow.providers.google.cloud.operators.email import EmailOperator
from airflow.utils.dates import days_ago
from google.cloud import bigquery

# Define your default args
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

# Initialize the DAG
dag = DAG(
    'dataproc_job_retry',
    default_args=default_args,
    description='A simple DAG to retry Dataproc job until success',
    schedule_interval=timedelta(minutes=5),
    start_date=days_ago(1),
    catchup=False,
)

# Define the Dataproc job
dataproc_job = {
    'reference': {'project_id': 'your-project-id'},
    'placement': {'cluster_name': 'your-cluster-name'},
    'hadoop_job': {
        'main_jar_file_uri': 'gs://your-bucket/your-jar.jar',
        'args': ['your-main-class', 'your-arguments']
    }
}

# Task to submit the Dataproc job
submit_dataproc_job = DataprocSubmitJobOperator(
    task_id='submit_dataproc_job',
    project_id='your-project-id',
    region='your-region',
    job=dataproc_job,
    gcp_conn_id='google_cloud_default',
    dag=dag,
)

# Task to wait for the Dataproc job to complete
wait_for_dataproc_job = DataprocJobSensor(
    task_id='wait_for_dataproc_job',
    project_id='your-project-id',
    region='your-region',
    job_id='{{ task_instance.xcom_pull(task_ids="submit_dataproc_job")["reference"]["job_id"] }}',
    dag=dag,
)

# Function to check BigQuery result
def check_bigquery_result(**kwargs):
    client = bigquery.Client()
    query = """
    SELECT COUNT(*) as count
    FROM `your-project-id.your_dataset.your_table`
    WHERE DATE(_PARTITIONTIME) = CURRENT_DATE()
    """
    query_job = client.query(query)
    results = query_job.result()
    for row in results:
        count = row['count']
        if count == 0:
            return 'submit_dataproc_job'
        else:
            return 'send_email'

# Task to check BigQuery result
check_result = PythonOperator(
    task_id='check_bigquery_result',
    python_callable=check_bigquery_result,
    provide_context=True,
    dag=dag,
)

# Dummy end task
end = DummyOperator(
    task_id='end',
    dag=dag,
)

# Task to send an email notification
send_email = EmailOperator(
    task_id='send_email',
    to='your_email@example.com',
    subject='Dataproc Job Completion',
    html_content='The Dataproc job has completed and the table is populated.',
    dag=dag,
)

# Define the task dependencies
submit_dataproc_job >> wait_for_dataproc_job >> check_result >> [submit_dataproc_job, send_email]
send_email >> end
