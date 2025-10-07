import os
import asyncio
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.sse import sse_client

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()


class TodoMCPClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
    async def connect_sse(self, url: str = "http://localhost:8001/sse"):
        """Connect to the MCP server via SSE."""
        sse_transport = await self.exit_stack.enter_async_context(sse_client(url))
        self.session = await self.exit_stack.enter_async_context(ClientSession(sse_transport[0], sse_transport[1]))
        
        # Initialize the connection
        await self.session.initialize()
        
        # List available tools
        response = await self.session.list_tools()
        print("Connected to MCP server. Available tools:")
        for tool in response.tools:
            print(f"  - {tool.name}: {tool.description}")
        print()
        
    async def disconnect(self):
        """Disconnect from the MCP server."""
        await self.exit_stack.aclose()
        
    async def process_query(self, user_message: str) -> str:
        """Process a user query using Claude and MCP tools."""
        messages = [{"role": "user", "content": user_message}]
        
        # Get available tools from MCP
        tools_response = await self.session.list_tools()
        
        # Convert MCP tools to Claude tool format
        claude_tools = []
        for tool in tools_response.tools:
            claude_tool = {
                "name": tool.name,
                "description": tool.description,
            }
            
            # Add input schema if available
            if hasattr(tool, 'inputSchema'):
                claude_tool["input_schema"] = tool.inputSchema
            
            claude_tools.append(claude_tool)
        
        print(f"User: {user_message}\n")
        
        # Agentic loop
        while True:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4096,
                tools=claude_tools,
                messages=messages
            )
            
            # Check if Claude wants to use a tool
            if response.stop_reason == "tool_use":
                # Add Claude's response to messages
                messages.append({"role": "assistant", "content": response.content})
                
                # Process tool calls
                tool_results = []
                for content_block in response.content:
                    if content_block.type == "tool_use":
                        tool_name = content_block.name
                        tool_input = content_block.input
                        
                        print(f"🔧 Calling tool: {tool_name}")
                        print(f"   Input: {tool_input}")
                        
                        # Call the MCP tool
                        result = await self.session.call_tool(tool_name, tool_input)
                        
                        print(f"   Result: {result.content}\n")
                        
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": content_block.id,
                            "content": str(result.content)
                        })
                
                # Add tool results to messages
                messages.append({"role": "user", "content": tool_results})
                
            elif response.stop_reason == "end_turn":
                # Extract the final text response
                final_response = ""
                for content_block in response.content:
                    if hasattr(content_block, "text"):
                        final_response += content_block.text
                
                print(f"Assistant: {final_response}\n")
                return final_response
            else:
                print(f"Unexpected stop reason: {response.stop_reason}")
                break
        
        return "Error processing query"


async def interactive_mode():
    """Run an interactive chat session."""
    client = TodoMCPClient()
    
    try:
        # Connect to MCP server
        server_url = os.getenv("MCP_SERVER_URL", "http://localhost:8001/sse")
        await client.connect_sse(server_url)
        
        print("=== Todo MCP Interactive Client ===")
        print("Type your requests or 'quit' to exit.\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye!")
                    break
                    
                if not user_input:
                    continue
                
                await client.process_query(user_input)
                
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}\n")
                
    finally:
        await client.disconnect()


async def single_query(query: str):
    """Run a single query and exit."""
    client = TodoMCPClient()
    
    try:
        server_url = os.getenv("MCP_SERVER_URL", "http://localhost:8001/sse")
        await client.connect_sse(server_url)
        result = await client.process_query(query)
        return result
    finally:
        await client.disconnect()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Single query mode
        query = " ".join(sys.argv[1:])
        asyncio.run(single_query(query))
    else:
        # Interactive mode
        asyncio.run(interactive_mode())

