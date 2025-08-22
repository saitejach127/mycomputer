# Wispr Clone

This project is a desktop application that allows you to record your voice with a global hotkey and get a transcription. The transcription is then automatically typed into your currently focused text field.

## Prerequisites

- [Docker](https://www.docker.com/get-started)
- [Conda](https://docs.conda.io/en/latest/miniconda.html) (Miniconda or Anaconda)

## Setup and Running the Application

Follow these steps to set up and run the application.

### 1. Start the Transcription Server

The server runs inside a Docker container.

**Build the Docker Image:**

Navigate to the `server` directory and run the following command to build the Docker image:

```bash
cd server
docker build -t wispr-flow-clone-server .
```

**Run the Docker Container:**

Run the following command to start the server. You can specify the `MODEL_SIZE` environment variable to choose the Whisper model you want to use (e.g., `tiny`, `base`, `small`, `medium`, `large`). The default is `base.en`.

```bash
docker run -d -p 5001:5000 -e MODEL_SIZE=base wispr-flow-clone-server
```

### 2. Set Up the Desktop Application

The desktop application is built with Python and Tkinter.

**Create the Conda Environment:**

Create a new conda environment for the desktop app:

```bash
conda create --name wispr-clone python=3.9 -y
```

**Activate the Environment:**

Activate the newly created environment:

```bash
conda activate wispr-clone
```

**Install Dependencies:**

Install the required Python packages:

```bash
pip install pynput sounddevice soundfile requests
```

### 3. Run the Desktop App

Make sure the server is running first. Then, from the `desktop-app` directory, run the following command to start the application:

```bash
cd desktop-app
python app.py
```

## How to Use

1.  Make sure the server and the desktop app are running.
2.  Click on any text field in any application.
3.  Press and hold the **Left Option/Alt key** to start recording your voice.
4.  Release the key to stop recording.
5.  The transcribed text will appear in the desktop app's window and will be automatically typed into the focused text field.
