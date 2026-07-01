import sqlite3

from config import DATA, JOBS, DB_PATH, DEMO_ACCOUNT_ID
from utils import now_ts

def db_connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    DATA.mkdir(parents=True, exist_ok=True)
    JOBS.mkdir(parents=True, exist_ok=True)
    with db_connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS accounts (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT,
                plan TEXT NOT NULL,
                quota_monthly INTEGER NOT NULL,
                created_at INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS jobs (
                job_id TEXT PRIMARY KEY,
                account_id TEXT NOT NULL,
                filename TEXT NOT NULL,
                storage_provider TEXT NOT NULL DEFAULT 'local',
                storage_key TEXT,
                storage_url TEXT,
                file_size INTEGER NOT NULL DEFAULT 0,
                mime_type TEXT,
                expires_at INTEGER,
                width INTEGER,
                height INTEGER,
                fps REAL,
                has_audio INTEGER NOT NULL DEFAULT 0,
                title TEXT,
                niche TEXT,
                objective TEXT,
                style TEXT NOT NULL DEFAULT 'classic',
                mode TEXT NOT NULL DEFAULT 'auto',
                target_length REAL NOT NULL DEFAULT 30,
                customer_request TEXT,
                duration REAL NOT NULL,
                clip_count INTEGER NOT NULL,
                status TEXT NOT NULL,
                created_at INTEGER NOT NULL,
                updated_at INTEGER NOT NULL,
                FOREIGN KEY (account_id) REFERENCES accounts(id)
            );

            CREATE TABLE IF NOT EXISTS suggestions (
                job_id TEXT NOT NULL,
                clip_id INTEGER NOT NULL,
                start REAL NOT NULL,
                duration REAL NOT NULL,
                hook TEXT NOT NULL,
                caption TEXT NOT NULL,
                cta TEXT NOT NULL,
                highlight_score INTEGER NOT NULL DEFAULT 50,
                reason TEXT,
                keywords TEXT,
                PRIMARY KEY (job_id, clip_id),
                FOREIGN KEY (job_id) REFERENCES jobs(job_id)
            );

            CREATE TABLE IF NOT EXISTS outputs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT NOT NULL,
                clip_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                url TEXT NOT NULL,
                created_at INTEGER NOT NULL,
                FOREIGN KEY (job_id) REFERENCES jobs(job_id)
            );

            CREATE TABLE IF NOT EXISTS editor_assets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT NOT NULL,
                asset_type TEXT NOT NULL,
                name TEXT NOT NULL,
                status TEXT NOT NULL,
                source TEXT,
                notes TEXT,
                created_at INTEGER NOT NULL,
                FOREIGN KEY (job_id) REFERENCES jobs(job_id)
            );

            CREATE TABLE IF NOT EXISTS editor_steps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT NOT NULL,
                clip_id INTEGER NOT NULL,
                step_order INTEGER NOT NULL,
                stage TEXT NOT NULL,
                title TEXT NOT NULL,
                status TEXT NOT NULL,
                notes TEXT,
                FOREIGN KEY (job_id, clip_id) REFERENCES suggestions(job_id, clip_id)
            );

            CREATE TABLE IF NOT EXISTS transcript_segments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT NOT NULL,
                start REAL NOT NULL,
                end REAL NOT NULL,
                text TEXT NOT NULL,
                confidence REAL,
                source TEXT NOT NULL,
                created_at INTEGER NOT NULL,
                FOREIGN KEY (job_id) REFERENCES jobs(job_id)
            );

            CREATE TABLE IF NOT EXISTS render_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT NOT NULL,
                clip_id INTEGER NOT NULL,
                status TEXT NOT NULL,
                attempts INTEGER NOT NULL DEFAULT 0,
                error TEXT,
                output_url TEXT,
                created_at INTEGER NOT NULL,
                updated_at INTEGER NOT NULL,
                FOREIGN KEY (job_id, clip_id) REFERENCES suggestions(job_id, clip_id)
            );
            """
        )
        existing_columns = {
            row["name"]
            for row in conn.execute("PRAGMA table_info(jobs)").fetchall()
        }
        suggestion_columns = {
            row["name"]
            for row in conn.execute("PRAGMA table_info(suggestions)").fetchall()
        }
        migrations = {
            "style": "ALTER TABLE jobs ADD COLUMN style TEXT NOT NULL DEFAULT 'classic'",
            "mode": "ALTER TABLE jobs ADD COLUMN mode TEXT NOT NULL DEFAULT 'auto'",
            "target_length": "ALTER TABLE jobs ADD COLUMN target_length REAL NOT NULL DEFAULT 30",
            "customer_request": "ALTER TABLE jobs ADD COLUMN customer_request TEXT",
            "storage_provider": "ALTER TABLE jobs ADD COLUMN storage_provider TEXT NOT NULL DEFAULT 'local'",
            "storage_key": "ALTER TABLE jobs ADD COLUMN storage_key TEXT",
            "storage_url": "ALTER TABLE jobs ADD COLUMN storage_url TEXT",
            "file_size": "ALTER TABLE jobs ADD COLUMN file_size INTEGER NOT NULL DEFAULT 0",
            "mime_type": "ALTER TABLE jobs ADD COLUMN mime_type TEXT",
            "expires_at": "ALTER TABLE jobs ADD COLUMN expires_at INTEGER",
            "width": "ALTER TABLE jobs ADD COLUMN width INTEGER",
            "height": "ALTER TABLE jobs ADD COLUMN height INTEGER",
            "fps": "ALTER TABLE jobs ADD COLUMN fps REAL",
            "has_audio": "ALTER TABLE jobs ADD COLUMN has_audio INTEGER NOT NULL DEFAULT 0",
        }
        for column, statement in migrations.items():
            if column not in existing_columns:
                conn.execute(statement)
        suggestion_migrations = {
            "highlight_score": "ALTER TABLE suggestions ADD COLUMN highlight_score INTEGER NOT NULL DEFAULT 50",
            "reason": "ALTER TABLE suggestions ADD COLUMN reason TEXT",
            "keywords": "ALTER TABLE suggestions ADD COLUMN keywords TEXT",
        }
        for column, statement in suggestion_migrations.items():
            if column not in suggestion_columns:
                conn.execute(statement)
        conn.execute(
            """
            INSERT OR IGNORE INTO accounts (id, name, email, plan, quota_monthly, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (DEMO_ACCOUNT_ID, "Demo Brand", "demo@ai-clip-agent.local", "MVP Trial", 50, now_ts()),
        )

def row_to_dict(row):
    return dict(row) if row else None
