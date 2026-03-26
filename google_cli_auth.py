import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.json.
# We just need to know who the user is to verify their identity.
SCOPES = [
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "openid",
]


def authenticate_cli():
    """Shows basic usage of the Google Auth OAuth2 flow for CLI."""
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Token expired. Refreshing...")
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Error refreshing token: {e}")
                creds = None

        if not creds:
            print("No valid token found. Starting Google Login flow...")
            try:
                # This requires the credentials.json file downloaded from Google Cloud Console
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                # This opens the browser!
                creds = flow.run_local_server(port=0)
            except FileNotFoundError:
                print(
                    "ERROR: 'credentials.json' not found. You must download it from the Google Cloud Console."
                )
                return None

        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return creds


def get_user_info(creds):
    """Retrieves the authenticated user's profile info."""
    try:
        # Build the oauth2 service
        service = build("oauth2", "v2", credentials=creds)
        user_info = service.userinfo().get().execute()
        return user_info
    except Exception as e:
        print(f"An error occurred retrieving user info: {e}")
        return None


if __name__ == "__main__":
    print("Initializing NSU Enterprise Security...\n")
    credentials = authenticate_cli()

    if credentials:
        user_profile = get_user_info(credentials)
        if user_profile:
            email = user_profile.get("email")
            name = user_profile.get("name")

            print(f"\n✅ Authentication Successful!")
            print(f"Welcome, {name} ({email})")

            # Example Domain Restriction
            if (
                "@northsouth.edu" in email or "mushfiq" in email.lower()
            ):  # Added fallback for your personal testing
                print("Access Granted: Authorized NSU User.")
            else:
                print("Access Denied: You must use an @northsouth.edu email address.")
                # os.remove('token.json') # Optionally force logout of invalid domain
        else:
            print("Failed to retrieve user profile.")
