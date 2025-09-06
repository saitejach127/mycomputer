from googleapiclient.discovery import build
import base64

def get_unread_emails(creds, limit=100):
    """Gets all unread emails up to a specified limit."""
    try:
        service = build('gmail', 'v1', credentials=creds)
        
        all_messages = []
        request = service.users().messages().list(userId='me', labelIds=['UNREAD'])
        
        while request is not None and len(all_messages) < limit:
            response = request.execute()
            messages = response.get('messages', [])
            all_messages.extend(messages)
            request = service.users().messages().list_next(previous_request=request, previous_response=response)

        if not all_messages:
            print("No unread messages found.")
            return []

        email_list = []
        # Process only up to the limit
        for message in all_messages[:limit]:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            subject = "(No Subject)"
            for header in msg['payload']['headers']:
                if header['name'] == 'Subject':
                    subject = header['value']
                    break
            email_list.append(subject)
        
        return email_list

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def get_latest_emails(creds, limit=100):
    """Gets the latest emails and their content."""
    try:
        service = build('gmail', 'v1', credentials=creds)
        
        # Get the list of latest messages
        results = service.users().messages().list(userId='me', maxResults=limit).execute()
        messages = results.get('messages', [])

        if not messages:
            print("No messages found.")
            return []

        email_list = []
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
            payload = msg['payload']
            headers = payload['headers']
            
            subject = next((header['value'] for header in headers if header['name'] == 'Subject'), '(No Subject)')
            sender = next((header['value'] for header in headers if header['name'] == 'From'), '(No Sender)')
            
            snippet = msg['snippet']
            
            body = ""
            if 'parts' in payload:
                for part in payload['parts']:
                    if part['mimeType'] == 'text/plain':
                        body_data = part['body'].get('data')
                        if body_data:
                            body = base64.urlsafe_b64decode(body_data).decode('utf-8')
                            break
            elif 'body' in payload and 'data' in payload['body']:
                 body_data = payload['body'].get('data')
                 if body_data:
                    body = base64.urlsafe_b64decode(body_data).decode('utf-8')


            email_list.append({
                'subject': subject,
                'from': sender,
                'snippet': snippet,
                'body': body
            })
            
        return email_list

    except Exception as e:
        print(f"An error occurred: {e}")
        return None
