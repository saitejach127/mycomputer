from googleapiclient.discovery import build
import datetime

def get_events_by_date_range(creds, start_date, end_date):
    """Gets events from the user's primary calendar within a specified date range.

    Args:
        creds: Google API credentials.
        start_date: Start date in 'YYYY-MM-DD' format.
        end_date: End date in 'YYYY-MM-DD' format.
    """
    try:
        service = build('calendar', 'v3', credentials=creds)

        # Convert dates to RFC3339 format
        time_min = datetime.datetime.strptime(start_date, '%Y-%m-%d').isoformat() + 'Z'
        time_max = datetime.datetime.strptime(end_date, '%Y-%m-%d').isoformat() + 'Z'

        print(f'Getting events from {start_date} to {end_date}')
        events_result = service.events().list(calendarId='primary', timeMin=time_min, timeMax=time_max,
                                              singleEvents=True, orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No events found in this date range.')
            return []

        event_list = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            event_list.append(f"{start} - {event['summary']}")
        
        return event_list

    except Exception as e:
        print(f"An error occurred: {e}")
        return None