
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


@app.route('/authorize')
def authorize():
    """Initiates the OAuth 2.0 authorization flow."""
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        prompt='consent',
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

    # Manually construct a dictionary from the credentials object that includes the id_token.
    creds_dict = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes,
        'id_token': flow.oauth2session.token['id_token']
    }
    creds_json_string = json.dumps(creds_dict)

    # Display the credentials to the user to copy
    return (f'<h1>Authentication Successful!</h1>'
            f'<p>Hello, {name} ({email}).</p>'
            f'<p>Please copy the text below and paste it into the desktop application:</p>'
            f'<textarea rows="10" cols="80" readonly>{creds_json_string}</textarea>'
            f'<p>You can now close this window.</p>')

if __name__ == '__main__':
    # It's recommended to use a production-ready WSGI server instead of the development server.
    app.run(port=5003, debug=True)
