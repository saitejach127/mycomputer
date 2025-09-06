from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io

def list_drive_files(creds, max_files=10):
    """Lists the last N modified files in the user's Google Drive."""
    try:
        service = build('drive', 'v3', credentials=creds)

        results = service.files().list(
            pageSize=max_files, 
            fields="nextPageToken, files(id, name, modifiedTime)",
            orderBy='modifiedTime desc').execute()
        
        items = results.get('files', [])

        if not items:
            print('No files found.')
            return []
        
        file_list = []
        for item in items:
            file_list.append(f"{item['name']} (ID: {item['id']})")
        
        return file_list

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def get_files_by_name(creds, filename):
    """Searches for files with a specific name."""
    try:
        service = build('drive', 'v3', credentials=creds)

        query = f"name = '{filename}'"
        results = service.files().list(
            q=query,
            pageSize=10, 
            fields="nextPageToken, files(id, name, modifiedTime)").execute()
        
        items = results.get('files', [])

        if not items:
            print(f'No files found with the name "{filename}".')
            return []
        
        file_list = []
        for item in items:
            file_list.append(f"{item['name']} (ID: {item['id']})")
        
        return file_list

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def create_file(creds, folder_name, file_name, content=None):
    """Creates a file in a specified folder in Google Drive, with optional content."""
    try:
        service = build('drive', 'v3', credentials=creds)

        # Find the folder ID
        folder_id = None
        query = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder'"
        results = service.files().list(q=query, pageSize=1, fields="files(id, name)").execute()
        items = results.get('files', [])
        if not items:
            return f"Folder '{folder_name}' not found."
        folder_id = items[0]['id']

        file_metadata = {
            'name': file_name,
            'parents': [folder_id]
        }
        
        media = None
        if content:
            media = MediaIoBaseUpload(io.BytesIO(content.encode('utf-8')), mimetype='text/plain', resumable=True)
        
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        return f"File '{file_name}' created with ID: {file.get('id')}"

    except Exception as e:
        return f"An error occurred: {e}"