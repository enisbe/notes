

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


from google.cloud import compute_v1

def check_instance_schedule(instance_name, project_id, zone):
    compute_client = compute_v1.InstancesClient()
    instance = compute_client.get(project=project_id, zone=zone, instance=instance_name)

    # Check labels
    labels = instance.labels
    if 'schedule' in labels:
        print(f"Instance {instance_name} has a scheduling label: {labels['schedule']}")

    # Check metadata
    metadata = instance.metadata
    for item in metadata.items:
        if 'schedule' in item.key:
            print(f"Instance {instance_name} has scheduling metadata: {item.key} = {item.value}")

project_id = 'your-project-id'
zone = 'your-zone'
instance_name = 'your-instance-name'

check_instance_schedule(instance_name, project_id, zone)






from google.cloud import compute_v1
import re

def extract_scheduler_name_from_resource_policies(project_id, zone, instance_name):
    compute_client = compute_v1.InstancesClient()
    instance = compute_client.get(project=project_id, zone=zone, instance=instance_name)

    # Check if instance has resource policies attached
    if instance.resource_policies:
        for policy_url in instance.resource_policies:
            # Extract the scheduler name from the URL
            match = re.search(r'/resourcePolicies/([^/]+)$', policy_url)
            if match:
                scheduler_name = match.group(1)
                print(f"Scheduler name extracted: {scheduler_name}")
    else:
        print(f"No resource policies found for instance '{instance_name}'.")

# Replace these variables with your actual project ID, zone, and instance name
project_id = 'your-project-id'
zone = 'your-zone'
instance_name = 'your-instance-name'

extract_scheduler_name_from_resource_policies(project_id, zone, instance_name)


from google.cloud import compute_v1

def list_all_instances(project_id):
    compute_client = compute_v1.InstancesClient()
    # The `aggregated_list` method returns a dictionary with zone names as keys and instances as values
    agg_list = compute_client.aggregated_list(project=project_id)

    for zone, response in agg_list:
        if response.instances:
            for instance in response.instances:
                print(f"Instance name: {instance.name}, Zone: {zone}, Status: {instance.status}")

# Replace 'your-project-id' with your actual Google Cloud project ID
project_id = 'your-project-id'
list_all_instances(project_id)
