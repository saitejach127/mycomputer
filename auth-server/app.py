
import flask
import os
import pickle
import json
import webbrowser

from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

# When running locally, disable OAuthlib's HTTPs verification.
# This is to be used for local testing only. Do not use in production.
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = flask.Flask(__name__)
app.secret_key = os.urandom(24)

# This is the path to the client secrets file.
CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "openid"
]
# The URI for the OAuth 2.0 callback. This must be authorized in the Google Cloud Console.
REDIRECT_URI = "http://localhost:5003/oauth2callback"

CREDENTIALS_DIR = "google_credentials"
USER_MAPPING_FILE = os.path.join(CREDENTIALS_DIR, "user_mapping.json")

@app.route('/authorize')
def authorize():
    """Initiates the OAuth 2.0 authorization flow."""
    if not os.path.exists(CREDENTIALS_DIR):
        os.makedirs(CREDENTIALS_DIR)

    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    
    # Store the state so we can verify it in the callback
    flask.session['state'] = state

    return flask.redirect(authorization_url)

@app.route('/oauth2callback')
def oauth2callback():
    """Callback route for Google OAuth 2.0."""
    state = flask.session['state']

    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI,
        state=state
    )

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = flask.request.url
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials
    
    # Get user info
    oauth2_client = build("oauth2", "v2", credentials=credentials)
    user_info = oauth2_client.userinfo().get().execute()
    
    email = user_info.get("email")
    name = user_info.get("name", "user")

    if email:
        # Save the credentials for the user
        safe_filename = "".join(c for c in email if c.isalnum() or c in "._-") + ".pkl"
        token_file = os.path.join(CREDENTIALS_DIR, safe_filename)

        with open(token_file, "wb") as token:
            pickle.dump(credentials, token)

        update_user_mapping(email, safe_filename)
        
        return f"""
        <h1>Authentication Successful!</h1>
        <p>Hello, {name} ({email}).</p>
        <p>You can now close this window and return to the application.</p>
        """
    else:
        return "<h1>Error: Could not retrieve user email.</h1>"

def update_user_mapping(email, pkl_filename):
    """Updates the JSON file that maps emails to their credential files."""
    mapping = {}
    if os.path.exists(USER_MAPPING_FILE):
        with open(USER_MAPPING_FILE, "r") as f:
            try:
                mapping = json.load(f)
            except json.JSONDecodeError:
                pass # File is empty or corrupt

    mapping[email] = pkl_filename
    
    with open(USER_MAPPING_FILE, "w") as f:
        json.dump(mapping, f, indent=4)

if __name__ == '__main__':
    # It's recommended to use a production-ready WSGI server instead of the development server.
    app.run(port=5003, debug=True)
