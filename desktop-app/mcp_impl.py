import json
import os
import asyncio
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Assuming mcp.config.json is in the same directory as this script
MCP_CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'mcp.config.json')

class MCPClientManager:
    def __init__(self):
        self.servers = {}
        self.sessions = {}
        self.exit_stack = AsyncExitStack()

    async def load_servers_from_config(self):
        """Loads server configurations from the mcp.config.json file."""
        if not os.path.exists(MCP_CONFIG_PATH):
            print(f"Error: MCP config file not found at {MCP_CONFIG_PATH}")
            return False
        
        with open(MCP_CONFIG_PATH, 'r') as f:
            try:
                config = json.load(f)
                self.servers = config.get('mcpServers', {})
                return True
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON from {MCP_CONFIG_PATH}: {e}")
                return False

    async def start_sessions(self):
        """Starts all server sessions defined in the config file concurrently."""
        if not await self.load_servers_from_config() or not self.servers:
            print("No valid MCP servers found to start.")
            return

        async def start_single_session(name, server_config):
            command = server_config.get('command')
            args = server_config.get('args', [])
            envs = server_config.get('envs', {})

            if not command:
                print(f"Skipping server '{name}' due to incomplete config.")
                return

            print(f"Starting MCP session for: {name}...")
            try:
                params = StdioServerParameters(command=command, args=args, envs=envs)
                
                # Use the exit stack to manage the lifecycle of the client and session
                read_stream, write_stream = await self.exit_stack.enter_async_context(stdio_client(params))
                session = await self.exit_stack.enter_async_context(ClientSession(read_stream, write_stream))
                
                await asyncio.wait_for(session.initialize(), timeout=10.0)

                self.sessions[name] = session
                print(f"Session for '{name}' started successfully.")
            except asyncio.TimeoutError:
                print(f"ERROR: Timeout starting session for '{name}'. It will be cleaned up on app exit.")
            except Exception as e:
                print(f"Failed to start session for '{name}': {e}")

        tasks = [start_single_session(name, config) for name, config in self.servers.items()]
        await asyncio.gather(*tasks)

    async def list_all_tools(self):
        """Lists all tools from all active sessions and returns them."""
        all_tools = {}
        if not self.sessions:
            print("No sessions are currently active.")
            return all_tools

        for name, session in self.sessions.items():
            tool_list = []
            try:
                tools_response = await session.list_tools()
                if tools_response and tools_response.tools:
                    for tool in tools_response.tools:
                        tool_list.append({"name": tool.name, "description": tool.description})
            except Exception as e:
                print(f"Failed to list tools for '{name}': {e}")

            all_tools[name] = tool_list
        return all_tools

    async def stop_sessions(self):
        """Stops all active MCP sessions and cleans up resources."""
        print("Stopping all MCP sessions and cleaning up resources...")
        await self.exit_stack.aclose()
        self.sessions = {}

async def main():
    """Main function to demonstrate MCP client usage."""
    manager = MCPClientManager()
    await manager.start_sessions()
    
    print("\nListing tools from all started sessions...")
    await manager.list_all_tools()
    
    # Remember to stop the sessions when done
    print("\nStopping all sessions...")
    await manager.stop_sessions()

if __name__ == "__main__":
    # This allows the async main function to be run.
    # In a real application, you would integrate this into your app's event loop.
    print("Running MCP Client standalone demo...")
    asyncio.run(main())
