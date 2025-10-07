# MCP Client for Todo Server

This directory contains client implementations that connect to the Todo MCP server via SSE (Server-Sent Events) and use AI models to interact with the todo list.

## Available Clients

### 1. OpenAI Client (`openai_client.py`)
Uses OpenAI's GPT-4 model to interact with your todo list.

### 2. Anthropic Client (`mcp_client.py`)
Uses Anthropic's Claude model to interact with your todo list.

## Setup

### 1. Install Dependencies

From the project root:
```bash
uv sync
```

### 2. Configure Environment Variables

Create a `.env` file in the project root with your API keys:

```env
# OpenAI API Key (for openai_client.py)
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic API Key (for mcp_client.py)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# MCP Server URL (optional, defaults to http://localhost:8001/sse)
MCP_SERVER_URL=http://localhost:8001/sse

# Server Configuration (for src/server.py)
HOST=localhost
PORT=8001
```

## Usage

### Start the MCP Server

First, start the todo MCP server in one terminal:

```bash
python src/server.py
```

The server will start on `http://localhost:8001`

### Run the OpenAI Client

In another terminal:

#### Interactive Mode
```bash
python client/openai_client.py
```

Then type your requests:
```
You: Create a todo to buy groceries
You: List all my todos
You: Mark todo 1 as completed
You: quit
```

#### Single Query Mode
```bash
python client/openai_client.py "Create a todo to finish the project report"
```

### Run the Anthropic Client

```bash
python client/mcp_client.py
```

Or for single queries:
```bash
python client/mcp_client.py "What todos do I have?"
```

## Example Interactions

### Creating Todos
```
You: Create a high priority todo to finish the quarterly report by Friday
🔧 Calling tool: create_todo
   Input: {'title': 'Finish the quarterly report', 'priority': 'high', 'due_date': '2025-10-10'}
   Result: ✅ Created todo: Finish the quarterly report (ID: 1)
