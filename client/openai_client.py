import os
import asyncio
import json
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession
from mcp.client.sse import sse_client

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class TodoMCPOpenAIClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
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
        """Process a user query using OpenAI and MCP tools."""
        messages = [{"role": "user", "content": user_message}]
        
        # Get available tools from MCP
        tools_response = await self.session.list_tools()
        
        # Convert MCP tools to OpenAI tool format
        openai_tools = []
        for tool in tools_response.tools:
            openai_tool = {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                }
            }
            
            # Add parameters schema if available
            if hasattr(tool, 'inputSchema'):
                openai_tool["function"]["parameters"] = tool.inputSchema
            
            openai_tools.append(openai_tool)
        
        print(f"User: {user_message}\n")
        
        # Agentic loop
        max_iterations = 10
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            
            response = self.client.chat.completions.create(
                model="gpt-5",
                messages=messages,
                tools=openai_tools,
                tool_choice="auto"
            )
            
            assistant_message = response.choices[0].message
            
            # Check if OpenAI wants to use tools
            if assistant_message.tool_calls:
                # Add assistant's response to messages
                messages.append({
                    "role": "assistant",
                    "content": assistant_message.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        } for tc in assistant_message.tool_calls
                    ]
                })
                
                # Process tool calls
                for tool_call in assistant_message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_input = json.loads(tool_call.function.arguments)
                    
                    print(f"🔧 Calling tool: {tool_name}")
                    print(f"   Input: {tool_input}")
                    
                    # Call the MCP tool
                    try:
                        result = await self.session.call_tool(tool_name, tool_input)
                        tool_result = str(result.content)
                        print(f"   Result: {tool_result}\n")
                    except Exception as e:
                        tool_result = f"Error calling tool: {str(e)}"
                        print(f"   Error: {tool_result}\n")
                    
                    # Add tool result to messages
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_result
                    })
                
            else:
                # No more tool calls, return the final response
                final_response = assistant_message.content or ""
                print(f"Assistant: {final_response}\n")
                return final_response
        
        return "Maximum iterations reached"


async def interactive_mode():
    """Run an interactive chat session."""
    client = TodoMCPOpenAIClient()
    
    try:
        # Connect to MCP server
        server_url = os.getenv("MCP_SERVER_URL", "http://localhost:8001/sse")
        await client.connect_sse(server_url)
        
        print("=== Todo MCP Interactive Client (OpenAI) ===")
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
    client = TodoMCPOpenAIClient()
    
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

