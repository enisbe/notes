import google.auth
from google.auth.transport.requests import Request
import requests
import json

# Configuration
project_id = "your-project-id"  # Replace with your project ID
location = "your-location"  # Replace with the location of your Composer environment
composer_environment = "your-composer-environment"  # Replace with your Composer environment name
dag_id = "your-dag-id"  # Replace with your DAG ID

# Get the access token
credentials, project = google.auth.default()
credentials.refresh(Request())
access_token = credentials.token

# Set the URL for triggering the DAG
url = f"https://composer.googleapis.com/v1/projects/{project_id}/locations/{location}/environments/{composer_environment}/dagRuns"

# Define the payload
payload = {
    "dagId": dag_id,
    "conf": {}  # Add any configuration parameters here if needed
}

# Set the headers
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

# Make the POST request to trigger the DAG
response = requests.post(url, headers=headers, data=json.dumps(payload))

# Check the response
if response.status_code == 200:
    print("DAG triggered successfully")
else:
    print(f"Failed to trigger DAG: {response.text}")
