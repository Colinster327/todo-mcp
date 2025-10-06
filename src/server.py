import os
from typing import Any, Dict, List
from mcp.server.fastmcp.server import FastMCP
from dotenv import load_dotenv
from db import get_db_connection, init_database


load_dotenv()


mcp = FastMCP(
    name="todo-mcp",
    host=os.getenv("HOST"),
    port=int(os.getenv("PORT"))
)


@mcp.tool()
def list_todos(completed: bool = None, priority: str = None, limit: int = 10) -> List[Dict[str, Any]]:
    """List all todos with optional filtering."""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT id, title, description, completed, created_at, updated_at, due_date, priority FROM todos"
    conditions = []
    params = []

    if completed is not None:
        conditions.append("completed = ?")
        params.append(1 if completed else 0)

    if priority:
        conditions.append("priority = ?")
        params.append(priority)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY created_at DESC"

    if limit:
        query += " LIMIT ?"
        params.append(limit)

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    # Convert to list of dictionaries
    todos = []
    for row in rows:
        id, title, description, completed, created_at, updated_at, due_date, priority = row
        todos.append({
            "id": id,
            "title": title,
            "description": description,
            "completed": bool(completed),
            "created_at": created_at,
            "updated_at": updated_at,
            "due_date": due_date,
            "priority": priority
        })

    return todos


@mcp.tool()
def create_todo(title: str, description: str = "", priority: str = "medium", due_date: str = None) -> Dict[str, Any]:
    """Create a new todo item."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO todos (title, description, priority, due_date) VALUES (?, ?, ?, ?)",
        (title, description, priority, due_date)
    )

    todo_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return {
        "id": todo_id,
        "title": title,
        "description": description,
        "priority": priority,
        "due_date": due_date,
        "completed": False,
        "message": f"✅ Created todo: {title} (ID: {todo_id})"
    }


@mcp.tool()
def update_todo(id: int, title: str = None, description: str = None, completed: bool = None,
                priority: str = None, due_date: str = None) -> Dict[str, Any]:
    """Update an existing todo item."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if todo exists
    cursor.execute("SELECT id FROM todos WHERE id = ?", (id,))
    if not cursor.fetchone():
        conn.close()
        return {"error": f"❌ Todo with ID {id} not found."}

    # Build update query dynamically
    updates = []
    params = []

    if title is not None:
        updates.append("title = ?")
        params.append(title)
    if description is not None:
        updates.append("description = ?")
        params.append(description)
    if completed is not None:
        updates.append("completed = ?")
        params.append(1 if completed else 0)
    if priority is not None:
        updates.append("priority = ?")
        params.append(priority)
    if due_date is not None:
        updates.append("due_date = ?")
        params.append(due_date)

    if not updates:
        conn.close()
        return {"error": "❌ No fields to update."}

    updates.append("updated_at = CURRENT_TIMESTAMP")
    params.append(id)

    query = f"UPDATE todos SET {', '.join(updates)} WHERE id = ?"
    cursor.execute(query, params)
    conn.commit()
    conn.close()

    return {"message": f"✅ Updated todo ID {id}"}


@mcp.tool()
def delete_todo(id: int) -> Dict[str, Any]:
    """Delete a todo item."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if todo exists
    cursor.execute("SELECT title FROM todos WHERE id = ?", (id,))
    todo = cursor.fetchone()

    if not todo:
        conn.close()
        return {"error": f"❌ Todo with ID {id} not found."}

    cursor.execute("DELETE FROM todos WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    return {"message": f"✅ Deleted todo: {todo[0]} (ID: {id})"}


@mcp.tool()
def get_todo(id: int) -> Dict[str, Any]:
    """Get a specific todo by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, title, description, completed, created_at, updated_at, due_date, priority FROM todos WHERE id = ?",
        (id,)
    )

    row = cursor.fetchone()
    conn.close()

    if not row:
        return {"error": f"❌ Todo with ID {id} not found."}

    id, title, description, completed, created_at, updated_at, due_date, priority = row

    return {
        "id": id,
        "title": title,
        "description": description,
        "completed": bool(completed),
        "created_at": created_at,
        "updated_at": updated_at,
        "due_date": due_date,
        "priority": priority
    }


if __name__ == "__main__":
    init_database()
    mcp.run(transport="sse")
