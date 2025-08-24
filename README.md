# Wispr Clone

This project is a desktop application that allows you to record your voice with a global hotkey and get a transcription. The transcription is then automatically typed into your currently focused text field.

## Prerequisites

- [Docker](https://www.docker.com/get-started)
- [Conda](https://docs.conda.io/en/latest/miniconda.html) (Miniconda or Anaconda)

---

## Setup and Running the Application

### 1. Authentication Setup (Google Credentials)

To use the Google integration features (Calendar, Drive, etc.), you need to generate your own `client_secret.json` file.

**Steps to Generate Credentials:**

1.  **Go to the Google Cloud Console**: Navigate to [https://console.cloud.google.com/](https://console.cloud.google.com/).
2.  **Create a New Project**: If you don't have one already, create a new project.
3.  **Enable APIs**: Go to the "APIs & Services" dashboard. Click "+ ENABLE APIS AND SERVICES" and enable the following APIs:
    *   Google Calendar API
    *   Google Drive API
    *   Gmail API
4.  **Configure OAuth Consent Screen**: Go to the "OAuth consent screen" tab. Choose "External" and create a consent screen. You only need to provide an app name, user support email, and developer contact information.
5.  **Create Credentials**: 
    *   Go to the "Credentials" tab and click "+ CREATE CREDENTIALS" -> "OAuth client ID".
    *   Select **Web Application** as the application type.
    *   Give it a name (e.g., "MyComputer Auth Server").
    *   Under **Authorized redirect URIs**, click "ADD URI" and enter exactly: `http://localhost:5003/oauth2callback`
6.  **Download JSON**: Click "CREATE". A window will pop up with your Client ID and Secret. Click **DOWNLOAD JSON** to get your `client_secret.json` file.

### 2. Start the Authentication Server

The auth server runs inside a Docker container and handles the Google login flow.

**Setup and Run:**

1.  **Place Credentials**: Move the `client_secret.json` file you just downloaded into the `auth-server/` directory.
2.  **Build the Docker Image**: Navigate to the `auth-server` directory and run:
    ```bash
    cd auth-server
    docker build -t mycomputer-auth-server .
    ```
3.  **Run the Docker Container**:
    ```bash
    docker run -p 5003:5003 -v "$(pwd)/google_credentials:/app/google_credentials" --name my-auth-server mycomputer-auth-server
    ```
    This will start the server and persist your login credentials on your local machine.

### 3. Start the Transcription Server

The transcription server also runs inside a Docker container.

**Build the Docker Image:**

Navigate to the `server` directory and run:

```bash
cd server
docker build -t wispr-flow-clone-server .
```

**Run the Docker Container:**

```bash
docker run -d -p 5001:5000 -e MODEL_SIZE=base wispr-flow-clone-server
```

### 4. Set Up and Run the Desktop Application

**Create the Conda Environment:**

```bash
conda create --name wispr-clone python=3.9 -y
conda activate wispr-clone
```

**Install Dependencies:**

Navigate to the `desktop-app` directory and install the required packages:
```bash
cd desktop-app
pip install -r requirements.txt
```

**Run the App:**

Make sure both servers are running. Then, from the `desktop-app` directory, run:

```bash
python app.py
```

## How to Use

1.  Make sure all servers and the desktop app are running.
2.  In the desktop app, go to the "Integrations" tab and click "Connect with Google".
3.  Your browser will open. Log in with your Google account and grant the requested permissions.
4.  Once you see the "Authentication Successful!" message, you can close the browser tab.
5.  Click on any text field in any application.
6.  Press and hold the **Left Option/Alt key** to start recording your voice.
7.  Release the key to stop recording.
8.  The transcribed text will be automatically typed into the focused text field.