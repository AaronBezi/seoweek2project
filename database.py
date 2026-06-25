import sqlite3

DB_NAME = "repos.db"


# creates the repos table if it doesn't already exist
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS repos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            language TEXT,
            stars INTEGER,
            readme TEXT,
            analysis TEXT
        )
    """)
    conn.commit()
    conn.close()


# inserts a new repo record into the database
def save_repo(repo_data):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO repos (owner, name, description, language, stars, readme)
        VALUES (:owner, :name, :description, :language, :stars, :readme)
    """, repo_data)
    conn.commit()
    conn.close()


# retrieves a repo record by owner and name
def get_repo(owner, name):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM repos WHERE owner = ? AND name = ?
    """, (owner, name))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


# updates the ai analysis field for an existing repo record
def update_analysis(owner, name, analysis):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE repos SET analysis = ? WHERE owner = ? AND name = ?
    """, (analysis, owner, name))
    conn.commit()
    conn.close()
