from googleapiclient.discovery import build
import datetime

def get_events_by_datetime_range(creds, start_datetime, end_datetime):
    """Gets events from the user's primary calendar within a specified datetime range.

    Args:
        creds: Google API credentials.
        start_datetime: Start datetime in ISO format (e.g., '2025-09-06T10:00:00Z').
        end_datetime: End datetime in ISO format (e.g., '2025-09-06T17:00:00Z').
    """
    try:
        service = build('calendar', 'v3', credentials=creds)

        print(f'Getting events from {start_datetime} to {end_datetime}')
        events_result = service.events().list(calendarId='primary', timeMin=start_datetime, timeMax=end_datetime,
                                              singleEvents=True, orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No events found in this datetime range.')
            return []

        event_list = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            event_list.append(f"{start} - {event['summary']}")
        
        return event_list

    except Exception as e:
        print(f"An error occurred: {e}")
        return None
