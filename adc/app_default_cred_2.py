import google.auth
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os


 
from google.oauth2.credentials import Credentials


# Define the scopes needed to get user profile information
SCOPES = [
    'openid',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
   # Included as per your original code
    # Note: The 'cloud-platform' scope was added in a later version you showed
]
# You had this line setting the path explicitly
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'C:\Users\enisb\AppData\Roaming\gcloud\application_default_credentials.json'
# os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'C:\Users\enisb\AppData\Roaming\gcloud\application_default_credentials.json'  # Set your ADC path here

def get_user_info_from_adc():
    """Loads ADC and fetches user info from the UserInfo endpoint."""
    user_email = 'N/A'
    user_name = 'N/A'
    credentials = None
    project_id = None # Added project_id variable for completeness

    try:
        # Load Application Default Credentials, requesting necessary scopes
        # This will find the file created by 'gcloud auth application-default login'
        print("Loading Application Default Credentials...")
        credentials, project_id = google.auth.default(scopes=SCOPES)
        # Added print statement from later debugging step for context
        print(f"Credentials loaded. Associated Project ID detected by library: {project_id}")

        # Check if credentials have an access token or need refreshing
        if not credentials.valid:
            if credentials.expired and credentials.refresh_token:
                print("Credentials expired, attempting refresh...")
                try:
                    credentials.refresh(Request())
                    print("Credentials refreshed successfully.")
                # Added specific exception handling from later version
                except google.auth.exceptions.RefreshError as re:
                     print(f"ERROR: Failed to refresh credentials: {re}")
                     return None, None
                except Exception as e:
                    print(f"Failed to refresh ADC credentials: {e}")
                    return None, None # Cannot proceed without valid credentials
            else:
                print("ADC credentials are not valid and cannot be refreshed.")
                # This might happen if the user revoked access or the refresh token is missing/invalid
                return None, None

        # If we have valid credentials, call the UserInfo API using the client library
        if credentials and credentials.valid:
            print("Credentials loaded successfully. Fetching user info...")
            try:
                # Build the service object for the UserInfo API using googleapiclient
                # userinfo_service = build('oauth2', 'v2', credentials=credentials)
                creds = Credentials(credentials.token, refresh_token=credentials.refresh_token, token_uri=credentials.token_uri, client_id=credentials.client_id, client_secret=credentials.client_secret)
                userinfo_service = build('oauth2', 'v2', credentials=creds, cache_discovery=False)

                # Execute the API call - THIS WAS THE LINE THAT FAILED with 403
                user_info = userinfo_service.userinfo().get().execute()

                # Extract info from the response dictionary
                user_email = user_info.get('email', 'N/A')
                user_name = user_info.get('name', 'N/A')
                print(f"User info obtained: Email={user_email}, Name={user_name}")
                return user_email, user_name

            except HttpError as http_err:
                # Original error handling path
                print(f"HTTP error fetching user info: {http_err}")
                # Added more specific checks from later version
                if hasattr(http_err, 'resp') and http_err.resp.status == 403:
                     print("Permission denied (403). Check IAM permissions AND token scopes.")
                     # Original message from traceback:
                     # print("Permission denied. Ensure the necessary scopes (openid, email, profile) were granted during 'gcloud auth application-default login'.")
                elif hasattr(http_err, 'resp') and http_err.resp.status == 401:
                     print("Authentication error (401). The credentials might be invalid or expired.")
                return None, None # Indicate failure
            except Exception as e:
                print(f"Error fetching user info from UserInfo endpoint: {e}")
                return None, None # Indicate failure
        else:
             print("Could not obtain valid ADC credentials.")
             return None, None

    except google.auth.exceptions.DefaultCredentialsError as e:
        print(f"Could not find or load Application Default Credentials: {e}")
        print("Please run 'gcloud auth application-default login' in your terminal.")
        return None, None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc() # Added for better general error reporting
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
