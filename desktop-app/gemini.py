import requests
import os
import copy
from litellm import completion


# def get_gemini_response(text, api_key, mcp_tools=None):
#     """
#     Sends a request to the Gemini API and returns the response.
#     """
#     if not api_key:
#         return "GEMINI_API_KEY not set."

#     headers = {
#         "x-goog-api-key": api_key,
#         "Content-Type": "application/json",
#     }
    
#     data = {
#         "contents": [{"parts": [{"text": text}]}],
#         "generationConfig": {"thinkingConfig": {"thinkingBudget": 0}},
#     }

#     try:
#         response = requests.post(
#             "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent",
#             headers=headers,
#             json=data
#         )
#         if response.status_code == 200:
#             result = response.json()
#             # TODO: Handle tool calls in the response
#             return result['candidates'][0]['content']['parts'][0]['text']
#         else:
#             # Return the full error from the API for better debugging
#             return f"Gemini API error: {response.status_code} - {response.text}"
#     except Exception as e:
#         return f"Error: {e}"

def get_gemini_response(text, api_key, mcp_tools=None):
    os.environ['GEMINI_API_KEY'] = api_key
    tools = []
    # mcp_tools is a dict of tool name to tool config
    if mcp_tools:
        for tool_name, tool_config in mcp_tools.items():
            tools.extend(tool_config)
    resp = completion(
        model="gemini/gemini-2.5-flash",
        messages=[{"role": "user", "content": "Get the latest JIRA Ticket of CEO Project with project key CEO and summarize it."}],
        reasoning_effort="low",
        tools=tools
    )
    print("Gemini Response:", resp )
    return resp['choices'][0]['message']['content']


