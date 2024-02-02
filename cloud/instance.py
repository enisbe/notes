

pip install google-cloud-scheduler google-cloud-compute

from google.cloud import scheduler_v1
from google.cloud import compute_v1

def list_scheduler_jobs(project_id, location):
    client = scheduler_v1.CloudSchedulerClient()
    parent = f"projects/{project_id}/locations/{location}"
    return client.list_jobs(request={"parent": parent})

def check_instance_in_scheduler_jobs(instance_name, project_id, location):
    jobs = list_scheduler_jobs(project_id, location)
    for job in jobs:
        # This part is pseudo-code and depends on how you set up your jobs
        # You might need to parse job.http_target or job.app_engine_http_target
        if instance_name in job.description:  # or any other relevant field
            print(f"Instance {instance_name} is targeted by Scheduler job: {job.name}")

project_id = "your-project-id"
location = "your-location"
instance_name = "your-instance-name"

check_instance_in_scheduler_jobs(instance_name, project_id, location)




# Retrieve basic instance information (including scheduling status)
request = compute.instances().get(project='your-project-id', zone='ZONE', instance='INSTANCE_NAME')
response = request.execute()

# Check if scheduling is enabled
scheduling_enabled = response['scheduling']['automaticRestart']

if scheduling_enabled:
  # Use CLI to get the actual schedule (assuming instance names align)
  schedule_output = subprocess.check_output(["gcloud", "compute", "instances", "describe", "INSTANCE_NAME", "--project", "your-project-id", "--format", "value(scheduling.automaticRestart.schedule)"]).decode("utf-8")
  print("Schedule:", schedule_output)
else:
  print("Instance is not attached to any schedule.")
