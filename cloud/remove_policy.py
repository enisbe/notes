from google.cloud import compute_v1
from google.oauth2 import service_account

# Credentials and Project Info
KEY_FILE_PATH = 'path/to/your/service-account-key.json'
PROJECT_ID = 'your-project-id'
ZONE = 'your-zone'  # e.g., 'us-central1-a'
REGION = 'us-central1'  # This should be just the region without the zone part

# Initialize the Compute Engine client
credentials = service_account.Credentials.from_service_account_file(KEY_FILE_PATH)
compute_client = compute_v1.InstancesClient(credentials=credentials)

# VM and Policy Details
VM_NAME = 'your-vm-name'
SCHEDULE_NAME = 'your-schedule-name'

def remove_resource_policies(project_id, zone, instance_name, policy_name):
    # Correctly identifying the full path of the policy to be removed
    policy_full_path = f"projects/{project_id}/regions/{zone[:-2]}/resourcePolicies/{policy_name}"

    # Create the request to remove resource policies
    request = compute_v1.RemoveResourcePoliciesInstanceRequest(
        project=project_id,
        zone=zone,
        instance=instance_name,
        instances_remove_resource_policies_request=compute_v1.InstancesRemoveResourcePoliciesRequest(
            resource_policies=[policy_full_path]
        ),
    )

    # Execute the request
    operation = compute_client.remove_resource_policies(request=request)
    return operation

# Example usage
operation = remove_resource_policies(PROJECT_ID, ZONE, VM_NAME, SCHEDULE_NAME)
print(f"Operation status: {operation.status}")
