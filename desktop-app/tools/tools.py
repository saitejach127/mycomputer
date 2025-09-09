from . import google_tools, atlassian_tools

def get_tools():
    google = google_tools.get_tools()
    atlassian = atlassian_tools.get_tools()
    return google + atlassian

def get_available_functions():
    google = google_tools.get_available_functions()
    atlassian = atlassian_tools.get_available_functions()
    return {**google, **atlassian}

def load_google_creds(email):
    return google_tools.load_google_creds(email)
