# Todo List MCP Server

A Model Context Protocol (MCP) server for managing todo lists with SQLite3 storage. This server provides tools for creating, reading, updating, and deleting todo items with support for priorities, due dates, and completion status.

## Features

- ✅ **Full CRUD Operations**: Create, read, update, and delete todos
- 🗃️ **SQLite3 Storage**: Persistent data storage in `~/.todo_mcp.db`
- 🏷️ **Priority Levels**: Low, medium, and high priority todos
- 📅 **Due Dates**: Optional due date support
- 🔍 **Filtering**: Filter todos by completion status and priority
- 📊 **Rich Display**: Emoji-enhanced output for better readability

## Installation

1. Install dependencies:
```bash
uv sync
```

2. Create environment file (optional):
```bash
# Create .env file with your preferred settings
echo "HOST=localhost" > .env
echo "PORT=8000" >> .env
```

3. Run the server:
```bash
python src/server.py
```

The server will run on `http://localhost:8000` by default (or use HOST/PORT from .env file).

## Available Tools

### 1. `list_todos`
List all todos with optional filtering.

**Parameters:**
- `completed` (boolean, optional): Filter by completion status
- `priority` (string, optional): Filter by priority level ("low", "medium", "high")
- `limit` (integer, optional): Limit number of results

**Example:**
```json
{
  "completed": false,
  "priority": "high",
  "limit": 10
}
```

### 2. `create_todo`
Create a new todo item.

**Parameters:**
- `title` (string, required): Title of the todo
- `description` (string, optional): Optional description
- `priority` (string, optional): Priority level ("low", "medium", "high") - defaults to "medium"
- `due_date` (string, optional): Due date in ISO format (YYYY-MM-DD)

**Example:**
```json
{
  "title": "Complete project documentation",
  "description": "Write comprehensive README and API docs",
  "priority": "high",
  "due_date": "2024-01-15"
}
```

### 3. `update_todo`
Update an existing todo item.

**Parameters:**
- `id` (integer, required): ID of the todo to update
- `title` (string, optional): New title
- `description` (string, optional): New description
- `completed` (boolean, optional): Completion status
- `priority` (string, optional): Priority level
- `due_date` (string, optional): Due date in ISO format

**Example:**
```json
{
  "id": 1,
  "completed": true,
  "priority": "low"
}
```

### 4. `delete_todo`
Delete a todo item.

**Parameters:**
- `id` (integer, required): ID of the todo to delete

**Example:**
```json
{
  "id": 1
}
```

### 5. `get_todo`
Get a specific todo by ID.

**Parameters:**
- `id` (integer, required): ID of the todo to retrieve

**Example:**
```json
{
  "id": 1
}
```

## Database Schema

The SQLite database contains a single `todos` table with the following structure:

```sql
CREATE TABLE todos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    due_date TIMESTAMP,
    priority TEXT DEFAULT 'medium' CHECK(priority IN ('low', 'medium', 'high'))
);
```

## Usage Examples

### Creating Todos
```bash
# Create a high priority todo
create_todo --title "Fix critical bug" --priority "high" --description "Fix the authentication bug in production"

# Create a todo with due date
create_todo --title "Submit report" --due_date "2024-01-20" --priority "medium"
```

### Listing Todos
```bash
# List all todos
list_todos

# List only incomplete high priority todos
list_todos --completed false --priority "high"

# List last 5 todos
list_todos --limit 5
```

### Updating Todos
```bash
# Mark todo as completed
update_todo --id 1 --completed true

# Change priority and add description
update_todo --id 2 --priority "low" --description "Updated description"
```

### Getting Todo Details
```bash
# Get specific todo details
get_todo --id 1
```

### Deleting Todos
```bash
# Delete a todo
delete_todo --id 1
```

## Error Handling

The server includes comprehensive error handling:
- Validates required parameters
- Checks for todo existence before updates/deletes
- Provides clear error messages with emoji indicators
- Handles database connection issues gracefully

## Data Storage

- Database file: `~/.todo_mcp.db`
- Automatic database initialization on first run
- SQLite3 for reliable, file-based storage
- Automatic timestamp tracking for created/updated dates

## Development

To run in development mode:

```bash
# Install dependencies
uv sync

# Run the server
python src/server.py
```

The server will automatically create the database and table structure on first run.
