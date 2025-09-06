from . import google_calendar, google_drive, google_mail, auth

def get_tools():
    return [
        {
            "type": "function",
            "function": {
                "name": "get_events_by_datetime_range",
                "description": "Gets events from the user's primary calendar within a specified datetime range.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "start_datetime": {
                            "type": "string",
                            "description": "Start datetime in ISO format (e.g., '2025-09-06T10:00:00Z')."
                        },
                        "end_datetime": {
                            "type": "string",
                            "description": "End datetime in ISO format (e.g., '2025-09-06T17:00:00Z')."
                        }
                    },
                    "required": ["start_datetime", "end_datetime"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "list_drive_files",
                "description": "Lists the last N modified files in the user's Google Drive.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "max_files": {
                            "type": "integer",
                            "description": "Maximum number of files to list. Defaults to 10."
                        }
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_files_by_name",
                "description": "Searches for files with a specific name.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filename": {
                            "type": "string",
                            "description": "The name of the file to search for."
                        }
                    },
                    "required": ["filename"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "create_file",
                "description": "Creates a file in a specified folder in Google Drive, with optional content.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "folder_name": {
                            "type": "string",
                            "description": "The name of the folder where the file will be created."
                        },
                        "file_name": {
                            "type": "string",
                            "description": "The name of the file to create."
                        },
                        "content": {
                            "type": "string",
                            "description": "The content to write to the file. Optional."
                        }
                    },
                    "required": ["folder_name", "file_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_unread_emails",
                "description": "Gets all unread emails up to a specified limit.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of unread emails to retrieve. Defaults to 100."
                        }
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_latest_emails",
                "description": "Gets the latest emails and their content.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of emails to retrieve. Defaults to 100."
                        }
                    }
                }
            }
        }
    ]

def get_available_functions():
    return {
        "get_events_by_datetime_range": google_calendar.get_events_by_datetime_range,
        "list_drive_files": google_drive.list_drive_files,
        "get_files_by_name": google_drive.get_files_by_name,
        "create_file": google_drive.create_file,
        "get_unread_emails": google_mail.get_unread_emails,
        "get_latest_emails": google_mail.get_latest_emails,
    }

def load_google_creds(email):
    return auth.load_credentials(email)
