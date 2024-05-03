from google.cloud import notebooks_v2

def start_instance_v2(project_id, location, instance_name):
    client = notebooks_v2.NotebookServiceClient()
    full_name = f"projects/{project_id}/locations/{location}/instances/{instance_name}"
    request = notebooks_v2.StartInstanceRequest(name=full_name)
    operation = client.start_instance(request=request)
    operation.result()  # Wait for the operation to complete
    print(f"Started instance: {full_name}")

def stop_instance_v2(project_id, location, instance_name):
    client = notebooks_v2.NotebookServiceClient()
    full_name = f"projects/{project_id}/locations/{location}/instances/{instance_name}"
    request = notebooks_v2.StopInstanceRequest(name=full_name)
    operation = client.stop_instance(request=request)
    operation.result()  # Wait for the operation to complete
    print(f"Stopped instance: {full_name}")

# Example usage
# start_instance_v2(PROJECT_ID, "us-central1-a", INSTANCE_NAME)
stop_instance_v2(PROJECT_ID, "us-central1-a", INSTANCE_NAME)
