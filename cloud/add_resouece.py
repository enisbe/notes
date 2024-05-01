from google.cloud import compute_v1
from google.oauth2 import service_account

# Credentials and Project Info
KEY_FILE_PATH = 'path/to/your/service-account-key.json'
PROJECT_ID = 'your-project-id'
ZONE = 'your-zone'  # e.g., 'us-central1-a'

# Initialize the Compute Engine client
credentials = service_account.Credentials.from_service_account_file(KEY_FILE_PATH)
compute_client = compute_v1.InstancesClient(credentials=credentials)

# VM and Policy Details
VM_NAME = 'your-vm-name'
SCHEDULE_NAME = 'your-schedule-name'

def add_resource_policies(project_id, zone, instance_name, policy_name):
    instance = compute_client.get(project=project_id, zone=zone, instance=instance_name)
    policies = list(instance.resource_policies)
    policies.append(f"projects/{project_id}/regions/{zone}/resourcePolicies/{policy_name}")
    
    # Preparing the request to add resource policies
    instance.set_resource_policies = compute_v1.SetResourcePoliciesInstanceRequest(
        project=project_id,
        zone=zone,
        instance=instance_name,
        instances_set_resource_policies_request_resource=compute_v1.InstancesSetResourcePoliciesRequest(
            resource_policies=policies
        ),
    )

    # Executing the request
    operation = compute_client.set_resource_policies(request=instance.set_resource_policies)
    return operation

# Example usage
operation = add_resource_policies(PROJECT_ID, ZONE, VM_NAME, SCHEDULE_NAME)
print(f"Operation status: {operation.status}")

