import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2 import id_token
import google.auth.transport.requests as google_requests

# The permissions we are asking Google for
SCOPES = ['openid', 'https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile']

class Color:
    BLUE = '\033[94m'
    GREEN = '\033[92m'   
    FAIL = '\033[91m'    
    END = '\033[0m'      
    BOLD = '\033[1m'

def authenticate_terminal():
    print(f"{Color.BLUE}🔒 Initiating Google CLI Authentication...{Color.END}")
    creds = None
    
    # Check if the terminal already remembers you from last time
    if os.path.exists('cli_token.json'):
        creds = Credentials.from_authorized_user_file('cli_token.json', SCOPES)
        
    # If no valid token, force the login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # This opens the browser automatically from the terminal!
            flow = InstalledAppFlow.from_client_secrets_file('google_credentials.json', SCOPES)
            creds = flow.run_local_server(port=8080)
            
        # Save the token to a hidden file so you don't have to log in every single time
        with open('cli_token.json', 'w') as token:
            token.write(creds.to_json())
            
    # Extract the email address securely
    request = google_requests.Request()
    user_info = id_token.verify_oauth2_token(
        creds.id_token, request, creds.client_id
    )
    return user_info.get('email')

if __name__ == '__main__':
    print(f"\n{Color.BOLD}======================================={Color.END}")
    print(f"{Color.BOLD} 🏛️ NSU Degree Audit Engine (CLI Mode) {Color.END}")
    print(f"{Color.BOLD}======================================={Color.END}\n")
    
    try:
        email = authenticate_terminal()
        print(f"{Color.GREEN}✅ Successfully authenticated as: {email}{Color.END}")
        print(f"🚀 CLI System Unlocked. Ready for execution.\n")
        
        # Here is where you would normally chain it to run your audit script
        print(f"{Color.BLUE}Type your command to run an audit (e.g., python3 auditL3mis.py test.csv){Color.END}\n")
        
    except Exception as e:
        print(f"\n{Color.FAIL}❌ CLI Authentication Failed: {e}{Color.END}")