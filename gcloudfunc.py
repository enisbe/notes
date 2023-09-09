import os
from google.cloud import notebooks_v1
from google.cloud.notebooks_v1.types import StartInstanceRequest

def start_notebook_instance(request):
    project_id = os.environ.get("GCP_PROJECT")
    location = 'YOUR_LOCATION'  # e.g., 'us-central1'
    instance_id = 'YOUR_INSTANCE_ID'  # Your Notebook instance ID
    
    client = notebooks_v1.NotebookServiceClient()
    
    instance_name = f"projects/{project_id}/locations/{location}/instances/{instance_id}"
    
    instance = client.get_instance(name=instance_name)
    
    if instance.state != notebooks_v1.Instance.State.RUNNING:
        start_request = StartInstanceRequest(name=instance_name)
        client.start_instance(request=start_request)
        return f"Instance {instance_id} started!", 200
    else:
        return f"Instance {instance_id} is already running.", 200


gcloud functions deploy start_notebook_instance \
--runtime python39 \
--trigger-http \
--allow-unauthenticated \
--service-account YOUR_SERVICE_ACCOUNT_EMAIL
