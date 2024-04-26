import os
from airflow import DAG
from airflow.providers.google.cloud.hooks.compute_ssh import ComputeEngineSSHHook
from airflow.providers.google.cloud.hooks.compute import ComputeEngineHook
from airflow.providers.google.cloud.operators.compute import ComputeEngineStartInstanceOperator

from airflow.providers.ssh.operators.ssh import SSHOperator
from datetime import datetime
from airflow.operators.python import PythonOperator


GCP_PROJECT_ID = os.environ.get('GCP_PROJECT_ID', 'sandbox-361003')
GCE_ZONE = os.environ.get('GCE_ZONE', 'us-central1-a')
GCE_INSTANCE = os.environ.get('GCE_INSTANCE', 'instance-20240425')


def remove_ssh_key(project_id, zone, instance_name, user):
    compute_hook = ComputeEngineHook(gcp_conn_id='google_cloud_default')
    instance_info = compute_hook.get_instance_info(
        zone=zone, resource_id=instance_name, project_id=project_id
    )

    metadata = instance_info['metadata']
    items = metadata.get('items', [])
    for item in items:
        if item.get('key') == 'ssh-keys':
            # Filter out the specific user's SSH keys
            filtered_keys = "\n".join(
                key for key in item["value"].split("\n") if not key.startswith(user + ":")
            )
            item["value"] = filtered_keys
            break

    compute_hook.set_instance_metadata(
        zone=zone, resource_id=instance_name, metadata=metadata, project_id=project_id
    )


default_args = {
    'start_date': datetime(2024, 4, 24),
}

dag = DAG(
    'gce_ssh_example',
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False
)


 # Task to start the instance
start_instance = ComputeEngineStartInstanceOperator(
    task_id="start_instance",
    project_id=GCP_PROJECT_ID,
    zone=GCE_ZONE,
    resource_id=GCE_INSTANCE,
    dag=dag,
)


vm_ssh = SSHOperator(
    task_id="execute_command_on_gce",
    ssh_hook=ComputeEngineSSHHook(
        instance_name=GCE_INSTANCE,
        user='jupyter',
        zone=GCE_ZONE,
        project_id=GCP_PROJECT_ID,
        use_oslogin=False,  # Set to True if using OS Login feature of GCE for SSH access
        # max_retries=10,
        use_iap_tunnel=False,  # Set to True to use IAP Tunneling for SSH
        use_internal_ip=False  # Set to True if connecting within the same network (VPC)
    ),
    # command="echo 'Hello World!'",  # Replace with your command
    command="./bash_scripts/execute_script2.sh",  # Replace with your command

    dag=dag
)


cleanup_ssh_key = PythonOperator(
    task_id='cleanup_ssh_key',
    python_callable=remove_ssh_key,
    op_kwargs={
        'project_id': GCP_PROJECT_ID,
        'zone': GCE_ZONE,
        'instance_name': GCE_INSTANCE,
        'user': 'jupyter'  # Change as needed
    },
    dag=dag
)


start_instance >> vm_ssh >> cleanup_ssh_key
