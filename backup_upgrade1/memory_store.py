
import sqlite3
import uuid
from pathlib import Path
from datetime import datetime, timezone

# ==========================================
# NEXUS AI - PERSISTENT MEMORY DATABASE
# ==========================================

# Database location
DB_PATH = Path(__file__).resolve().parent / "nexus_memory.db"


# ==========================================
# DATABASE CONNECTION
# ==========================================

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def current_time():
    return datetime.now(timezone.utc).isoformat()


# ==========================================
# INITIALIZE DATABASE
# ==========================================

def init_db():

    with get_connection() as conn:

        # Store conversations
        conn.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        # Store individual messages
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (conversation_id)
                    REFERENCES conversations(id)
                    ON DELETE CASCADE
            )
        """)

        # Store personal memories
        conn.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memory_key TEXT NOT NULL UNIQUE,
                memory_value TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        # Improve message lookup speed
        conn.execute("""
            CREATE INDEX IF NOT EXISTS
            idx_messages_conversation
            ON messages(conversation_id)
        """)


# ==========================================
# CONVERSATION MANAGEMENT
# ==========================================

def create_conversation(title="New Conversation"):

    conversation_id = str(uuid.uuid4())
    timestamp = current_time()

    with get_connection() as conn:
        conn.execute("""
            INSERT INTO conversations
            (id, title, created_at, updated_at)
            VALUES (?, ?, ?, ?)
        """, (
            conversation_id,
            title,
            timestamp,
            timestamp
        ))

    return conversation_id


def save_message(conversation_id, role, content):

    timestamp = current_time()

    with get_connection() as conn:

        conn.execute("""
            INSERT INTO messages
            (conversation_id, role, content, created_at)
            VALUES (?, ?, ?, ?)
        """, (
            conversation_id,
            role,
            content,
            timestamp
        ))

        conn.execute("""
            UPDATE conversations
            SET updated_at = ?
            WHERE id = ?
        """, (timestamp, conversation_id))


def get_messages(conversation_id):

    with get_connection() as conn:

        rows = conn.execute("""
            SELECT role, content, created_at
            FROM messages
            WHERE conversation_id = ?
            ORDER BY id ASC
        """, (conversation_id,)).fetchall()

    return [dict(row) for row in rows]


def list_conversations(limit=50):

    with get_connection() as conn:

        rows = conn.execute("""
            SELECT id, title, created_at, updated_at
            FROM conversations
            ORDER BY updated_at DESC
            LIMIT ?
        """, (limit,)).fetchall()

    return [dict(row) for row in rows]


def rename_conversation(conversation_id, title):

    with get_connection() as conn:

        conn.execute("""
            UPDATE conversations
            SET title = ?, updated_at = ?
            WHERE id = ?
        """, (title, current_time(), conversation_id))


def delete_conversation(conversation_id):

    with get_connection() as conn:

        conn.execute("""
            DELETE FROM conversations
            WHERE id = ?
        """, (conversation_id,))


# ==========================================
# PERSONAL MEMORY MANAGEMENT
# ==========================================

def save_memory(memory_key, memory_value):

    timestamp = current_time()

    with get_connection() as conn:

        conn.execute("""
            INSERT INTO memories
            (memory_key, memory_value, created_at, updated_at)
            VALUES (?, ?, ?, ?)

            ON CONFLICT(memory_key)
            DO UPDATE SET
                memory_value = excluded.memory_value,
                updated_at = excluded.updated_at
        """, (
            memory_key,
            memory_value,
            timestamp,
            timestamp
        ))


def get_memories(limit=100):

    with get_connection() as conn:

        rows = conn.execute("""
            SELECT id, memory_key, memory_value, created_at
            FROM memories
            ORDER BY updated_at DESC
            LIMIT ?
        """, (limit,)).fetchall()

    return [dict(row) for row in rows]


def delete_memory(memory_id):

    with get_connection() as conn:

        conn.execute("""
            DELETE FROM memories
            WHERE id = ?
        """, (memory_id,))


# ==========================================
# DATABASE STATISTICS
# ==========================================

def get_database_stats():

    with get_connection() as conn:

        conversations = conn.execute(
            "SELECT COUNT(*) FROM conversations"
        ).fetchone()[0]

        messages = conn.execute(
            "SELECT COUNT(*) FROM messages"
        ).fetchone()[0]

        memories = conn.execute(
            "SELECT COUNT(*) FROM memories"
        ).fetchone()[0]

    return {
        "conversations": conversations,
        "messages": messages,
        "memories": memories
    }
