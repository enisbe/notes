import datetime
from airflow import DAG
from airflow.providers.google.cloud.operators.dataproc import (
    DataprocCreateClusterOperator,
    DataprocSubmitJobOperator,
    DataprocDeleteClusterOperator
)

PROJECT_ID = 'your-project-id'
CLUSTER_NAME = 'your-cluster-name'
REGION = 'your-gcp-region'  # e.g., 'us-central1'
BUCKET_NAME = 'your-gcs-bucket'

# Cluster configuration details (Adjust as needed)
CLUSTER_CONFIG = {
    "master_config": {
        "num_instances": 1,
        "machine_type_uri": "n1-standard-2",
    },
    "worker_config": {
        "num_instances": 2,
        "machine_type_uri": "n1-standard-2",
    },
}

# Example PySpark job 
PYSPARK_JOB = {
    "reference": {"project_id": PROJECT_ID},
    "placement": {"cluster_name": CLUSTER_NAME},
    "pyspark_job": {
        "main_python_file_uri": f"gs://{BUCKET_NAME}/wordcount.py"
    },
}

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime.datetime(2024, 4, 1) 
}

with DAG(
    dag_id='dataproc_job_pipeline',
    default_args=default_args,
    schedule_interval=None 
) as dag:

    create_cluster = DataprocCreateClusterOperator(
        task_id="create_cluster",
        project_id=PROJECT_ID,
        cluster_config=CLUSTER_CONFIG,
        region=REGION,
        cluster_name=CLUSTER_NAME,
    )

    submit_job = DataprocSubmitJobOperator(
        task_id="submit_job", 
        job=PYSPARK_JOB, 
        location=REGION, 
        project_id=PROJECT_ID
    )

    delete_cluster = DataprocDeleteClusterOperator(
        task_id="delete_cluster",
        project_id=PROJECT_ID,
        cluster_name=CLUSTER_NAME,
        region=REGION,
        trigger_rule='all_done' 
    )

    create_cluster >> submit_job >> delete_cluster
