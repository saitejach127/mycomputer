import requests
import os
import copy
from litellm import completion
import asyncio
import json

def get_gemini_response(text, api_key, mcp_tools=None, mcp_manager=None):
    os.environ['GEMINI_API_KEY'] = api_key
    
    tools = []
    tool_to_session_map = {}
    tool_to_server_map = {}

    if mcp_tools and mcp_manager:
        for server_name, tool_config in mcp_tools.items():
            tools.extend(tool_config)
            session = mcp_manager.sessions.get(server_name)
            if session:
                for tool in tool_config:
                    tool_name = tool.get('function', {}).get('name')
                    if tool_name:
                        tool_to_session_map[tool_name] = session
                        tool_to_server_map[tool_name] = server_name

    messages=[{"role": "user", "content": text}]

    resp = completion(
        model="gemini/gemini-2.5-flash",
        messages=messages,
        tools=tools
    )
    # print("Initial response:", resp )
    if resp.choices[0].message.tool_calls:
        tool_calls = resp.choices[0].message.tool_calls
        
        async def process_tool_calls():
            tool_responses = []
            for tool_call in tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                print(f"Calling tool: {tool_name} with args: {tool_args}")
                
                session = tool_to_session_map.get(tool_name)
                if session:
                    try:
                        print(f"Starting tool call for {tool_name}")
                        result = await asyncio.wait_for(session.call_tool(tool_name, tool_args), timeout=30.0)
                        print(f"Done tool call for {tool_name}")
                        tool_responses.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": tool_name,
                            "content": result.response,
                        })
                    except asyncio.TimeoutError:
                        print(f"ERROR: Timeout calling tool {tool_name}")
                        tool_responses.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": tool_name,
                            "content": f"Error: Timeout calling tool {tool_name}",
                        })
                    except Exception as e:
                        print(f"ERROR: calling tool {tool_name}: {e}")
                        tool_responses.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": tool_name,
                            "content": f"Error calling tool: {e}",
                        })
            return tool_responses

        try:
            tool_outputs = asyncio.run(process_tool_calls())
        except Exception as e:
            print(f"ERROR: processing tool calls: {e}")
            tool_outputs = []
        
        messages.append(resp.choices[0].message)
        messages.extend(tool_outputs)
        print("Messages after tool calls:", messages )
        resp = completion(
            model="gemini/gemini-2.5-flash",
            messages=messages,
            tools=tools
        )
        # print("Final response after tool calls:", resp )
    return resp['choices'][0]['message']['content']


