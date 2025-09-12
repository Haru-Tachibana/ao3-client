import sqlite3
from rich.console import Console

console = Console()
DB_FILE = "bookmarks.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS bookmarks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            url TEXT
        )
    """)
    conn.commit()
    conn.close()

def add_bookmark(url, title):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("INSERT INTO bookmarks (title, url) VALUES (?, ?)", (title, url))
    conn.commit()
    conn.close()
    console.print(f"[green]Bookmarked:[/green] {title} ({url})")

def list_bookmarks():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT id, title, url FROM bookmarks")
    rows = cur.fetchall()
    conn.close()

    if not rows:
        console.print("[yellow]No bookmarks yet.[/yellow]")
        return

    console.print("[bold underline cyan]Bookmarks[/bold underline cyan]:")
    for row in rows:
        console.print(f"{row[0]}. [cyan]{row[1]}[/cyan] - {row[2]}")
