import os
from jira import JIRA
from dotenv import load_dotenv

load_dotenv()

JIRA_SERVER = os.getenv("JIRA_SERVER")
JIRA_USERNAME = os.getenv("JIRA_USERNAME")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")

jira = JIRA(server=JIRA_SERVER, basic_auth=(JIRA_USERNAME, JIRA_API_TOKEN))

def get_tools():
    return [
        {
            "type": "function",
            "function": {
                "name": "jira_get_issue",
                "description": "Get details of a specific Jira issue.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "issue_key": {
                            "type": "string",
                            "description": "The key of the Jira issue (e.g., 'PROJ-123')."
                        }
                    },
                    "required": ["issue_key"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "jira_search",
                "description": "Search for Jira issues using JQL.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "jql": {
                            "type": "string",
                            "description": "The JQL query to use for the search."
                        }
                    },
                    "required": ["jql"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "jira_create_issue",
                "description": "Create a new Jira issue.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "summary": {
                            "type": "string",
                            "description": "The summary or title of the new issue."
                        },
                        "description": {
                            "type": "string",
                            "description": "The detailed description of the new issue."
                        },
                        "project_key": {
                            "type": "string",
                            "description": "The key of the project where the issue will be created."
                        },
                        "issue_type": {
                            "type": "string",
                            "description": "The type of the issue (e.g., 'Task', 'Bug'). Defaults to 'Task'."
                        }
                    },
                    "required": ["summary", "description", "project_key"]
                }
            }
        }
    ]

def get_available_functions():
    return {
        "jira_get_issue": jira_get_issue,
        "jira_search": jira_search,
        "jira_create_issue": jira_create_issue,
    }

def jira_get_issue(issue_key):
    """
    Get details of a specific issue.
    """
    try:
        issue = jira.issue(issue_key)
        return {
            "summary": issue.fields.summary,
            "description": issue.fields.description,
            "status": issue.fields.status.name,
            "assignee": issue.fields.assignee.displayName if issue.fields.assignee else "Unassigned",
        }
    except Exception as e:
        return str(e)

def jira_search(jql):
    """
    Search issues using JQL.
    """
    try:
        issues = jira.search_issues(jql)
        return [
            {
                "key": issue.key,
                "summary": issue.fields.summary,
                "status": issue.fields.status.name,
            }
            for issue in issues
        ]
    except Exception as e:
        return str(e)

def jira_create_issue(summary, description, project_key, issue_type="Task"):
    """
    Create a new issue.
    """
    try:
        issue_dict = {
            "project": {"key": project_key},
            "summary": summary,
            "description": description,
            "issuetype": {"name": issue_type},
        }
        new_issue = jira.create_issue(fields=issue_dict)
        return new_issue.key
    except Exception as e:
        return str(e)
