import google.auth
from google.auth.transport.requests import Request
# Remove googleapiclient imports as they are not needed for the direct request method
# from googleapiclient.discovery import build
# from googleapiclient.errors import HttpError
import requests # Import the requests library
import os
import sys # To potentially exit cleanly on critical credential errors

# Define the scopes needed to get user profile information
# Note: 'cloud-platform' is very broad and not strictly required for userinfo.
# openid, email, profile are sufficient for the userinfo endpoint.
SCOPES = [
    'openid',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/cloud-platform' # Included as per your original code
]
# Set the environment variable if needed (usually google.auth.default finds it automatically)
# os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'C:\Users\enisb\AppData\Roaming\gcloud\application_default_credentials.json'

def get_user_info_from_adc():
    """Loads ADC and fetches user info directly from the UserInfo endpoint using requests."""
    user_email = 'N/A'
    user_name = 'N/A'
    credentials = None
    project_id = None

    try:
        # Load Application Default Credentials, requesting necessary scopes
        print("Loading Application Default Credentials...")
        credentials, project_id = google.auth.default(scopes=SCOPES)
        print(f"Credentials loaded. Associated Project ID detected by library: {project_id}")

        # Check if credentials have an access token or need refreshing
        if not credentials.valid:
            if credentials.expired and credentials.refresh_token:
                print("Credentials expired, attempting refresh...")
                try:
                    credentials.refresh(Request())
                    print("Credentials refreshed successfully.")
                except google.auth.exceptions.RefreshError as re:
                     print(f"ERROR: Failed to refresh credentials: {re}")
                     # Depending on severity, you might exit or just return None
                     return None, None # Cannot proceed without valid credentials
                except Exception as e:
                    print(f"Failed to refresh ADC credentials: {e}")
                    return None, None # Cannot proceed without valid credentials
            else:
                print("ADC credentials are not valid and cannot be refreshed.")
                # This might happen if the user revoked access or the refresh token is missing/invalid
                return None, None

        # If we have valid credentials, call the UserInfo API directly using requests
        if credentials and credentials.valid:
            # Ensure we actually have an access token after potential refresh
            if not credentials.token:
                print("Could not get access token from credentials after refresh.")
                return None, None

            print("Credentials valid. Fetching user info via direct HTTPS request...")
            try:
                access_token = credentials.token
                headers = {'Authorization': f'Bearer {access_token}'}
                userinfo_url = 'https://www.googleapis.com/oauth2/v2/userinfo' # Standard endpoint

                response = requests.get(userinfo_url, headers=headers)

                # Check if the request was successful
                if response.ok: # status_code < 400
                    user_info = response.json() # Parse the JSON response
                    user_email = user_info.get('email', 'N/A')
                    user_name = user_info.get('name', 'N/A')
                    print(f"User info obtained: Email={user_email}, Name={user_name}")
                    return user_email, user_name
                else:
                    # Request failed, print error details
                    print(f"HTTP error fetching user info directly: Status Code={response.status_code}")
                    print(f"Response Body: {response.text}")
                    # Specific handling for common errors
                    if response.status_code == 403:
                        print("Permission denied (403). Check IAM permissions AND token scopes.")
                    elif response.status_code == 401:
                        print("Authentication error (401). Credentials might be invalid/expired or lack necessary scopes.")
                    return None, None # Indicate failure

            except requests.exceptions.RequestException as req_err:
                 print(f"Network error during direct HTTPS request: {req_err}")
                 return None, None # Indicate failure
            except Exception as e:
                 print(f"Error parsing user info response or other issue: {e}")
                 return None, None # Indicate failure
        else:
            # This case should theoretically be caught by the earlier checks, but good to have
             print("Could not obtain valid ADC credentials.")
             return None, None

    except google.auth.exceptions.DefaultCredentialsError as e:
        print(f"Could not find or load Application Default Credentials: {e}")
        print("Please run 'gcloud auth application-default login' in your terminal.")
        return None, None
    except Exception as e:
        # Catch-all for unexpected errors during credential loading/handling
        print(f"An unexpected error occurred during credential handling: {e}")
        import traceback
        traceback.print_exc() # Print full traceback for unexpected errors
        return None, None

# Example usage:
if __name__ == "__main__":
    email, name = get_user_info_from_adc()
    if email and name and email != 'N/A': # Check if valid data was returned
        print(f"\nSuccessfully retrieved user info:")
        print(f"  Email: {email}")
        print(f"  Name: {name}")
    else:
        print("\nFailed to retrieve user info using ADC.")
