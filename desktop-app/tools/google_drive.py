from googleapiclient.discovery import build

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
