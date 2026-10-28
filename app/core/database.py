import sqlite3
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from app.core.config import settings

class Database:
    def __init__(self, db_path: str = "devpilot.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        cur.execute('''CREATE TABLE IF NOT EXISTS repositories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT UNIQUE NOT NULL,
            name TEXT,
            registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        cur.execute('''CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            repo_id INTEGER,
            description TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            plan TEXT,
            diff TEXT,
            files_inspected TEXT,
            files_changed TEXT,
            patch_summary TEXT,
            approved BOOLEAN DEFAULT 0,
            approved_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (repo_id) REFERENCES repositories (id)
        )''')
        
        cur.execute('''CREATE TABLE IF NOT EXISTS test_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER,
            test_name TEXT,
            status TEXT,
            output TEXT,
            duration REAL,
            executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (task_id) REFERENCES tasks (id)
        )''')
        
        conn.commit()
        conn.close()
    
    def register_repo(self, path: str, name: str = None):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO repositories (path, name) VALUES (?, ?)", (path, name))
            repo_id = cur.lastrowid
            conn.commit()
            return repo_id
        except sqlite3.IntegrityError:
            cur.execute("SELECT id FROM repositories WHERE path = ?", (path,))
            row = cur.fetchone()
            return row[0] if row else None
        finally:
            conn.close()
    
    def get_repo(self, repo_id: int):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM repositories WHERE id = ?", (repo_id,))
        row = cur.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def create_task(self, repo_id: int, description: str):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("INSERT INTO tasks (repo_id, description) VALUES (?, ?)", (repo_id, description))
        task_id = cur.lastrowid
        conn.commit()
        conn.close()
        return task_id
    
    def update_task(self, task_id: int, **kwargs):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        fields = []
        values = []
        for k, v in kwargs.items():
            if isinstance(v, (list, dict)):
                v = json.dumps(v)
            fields.append(f"{k} = ?")
            values.append(v)
        values.append(task_id)
        cur.execute(f"UPDATE tasks SET {', '.join(fields)} WHERE id = ?", values)
        conn.commit()
        conn.close()
    
    def get_task(self, task_id: int):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = cur.fetchone()
        conn.close()
        if row:
            task = dict(row)
            for field in ['files_inspected', 'files_changed']:
                if task.get(field):
                    try:
                        task[field] = json.loads(task[field])
                    except:
                        task[field] = []
            return task
        return None
    
    def add_test_result(self, task_id: int, test_name: str, status: str, output: str, duration: float):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("INSERT INTO test_results (task_id, test_name, status, output, duration) VALUES (?, ?, ?, ?, ?)",
                    (task_id, test_name, status, output, duration))
        conn.commit()
        conn.close()
    
    def get_test_results(self, task_id: int):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM test_results WHERE task_id = ?", (task_id,))
        rows = cur.fetchall()
        conn.close()
        return [dict(row) for row in rows]

db = Database()
