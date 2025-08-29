from googleapiclient.discovery import build

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