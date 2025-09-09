import os
import json
from litellm import completion
import datetime
from tools.tools import get_tools, get_available_functions, load_google_creds

def get_gemini_response(text, api_key, email, messages=None):
    os.environ['GEMINI_API_KEY'] = api_key
    creds = load_google_creds(email)
    if not creds:
        return "Could not load Google credentials. Please check your configuration.", None

    if messages is None:
        messages = [{"role": "system", "content": f"Today date is {datetime.datetime.now().strftime('%d %b %Y')} and time is {datetime.datetime.now().strftime('%H:%M:%S')}. You answer everything not just google services. use google services only if you dont know something or want to do something. You are a helpful assistant who does things without asking many questions.  Always use the tools when you need to get information or perform actions related to Google services. If you don't know the answer, use the tools to find out. Be concise and to the point."}]
    
    messages.append({"role": "user", "content": text})
    
    tools = get_tools()
    available_functions = get_available_functions()

    while True:
        resp = completion(
            model="gemini/gemini-2.5-flash",
            messages=messages,
            tools=tools
        )

        choice = resp.choices[0]
        if choice.finish_reason == "tool_calls":
            tool_calls = choice.message.tool_calls
            messages.append(choice.message) # Add the assistant's message with tool calls to the history
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_to_call = available_functions[function_name]
                function_args = json.loads(tool_call.function.arguments)
                
                # Add credentials to the arguments
                if function_name in ["get_events_by_datetime_range", "list_drive_files", "get_files_by_name", "get_unread_emails", "create_file", "get_latest_emails"]:
                    function_args['creds'] = creds
                
                function_response = function_to_call(**function_args)
                
                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": json.dumps(function_response),
                })
        else:
            messages.append(choice.message)
            return choice.message.content, messages
