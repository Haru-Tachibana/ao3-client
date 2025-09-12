# AO3 Client (Terminal)

A simple terminal-based client for browsing and reading [Archive of Our Own (AO3)](https://archiveofourown.org) fanfics from your terminal. The project is cross-platform and should work on any system with Python 3.9+, though it has been tested on macOS (Apple Silicon / M4) with Python 3.13.5.

---

## Features

* 🔍 Search AO3 works by tags, ships, and keywords
* 📑 Filter results (rating, completed-only, sort by kudos/hits/date)
* 📖 Read full works or chapters in your terminal
* 📌 Bookmark works locally (SQLite)
* 🗂️ List & manage saved bookmarks

---

## Requirements

* Python 3.9+ (tested with 3.13.5 on macOS M4)
* Git (for cloning)
* Terminal / command line access

> This README provides OS-neutral instructions. Tested on macOS, but should work on Linux and Windows with Python 3.9+.

---

## Project layout

```
ao3-client/
│── venv/                  # virtual environment (ignored by git)
│── ao3/                   # package source
│   │── __init__.py
│   │── cli.py             # main CLI entrypoint
│   │── reader.py
│   │── db.py
│   │── utils.py
│
│── requirements.txt
│── setup.py
│── README.md
│── .gitignore
```

> Make sure `ao3/__init__.py` exists (can be empty). This allows `python -m ao3.cli` to work.

---

## Detailed Setup (cross-platform)

### 1) Clone the repository

```bash
git clone https://github.com/<your-username>/ao3-client.git
cd ao3-client
```

### 2) Create a virtual environment

```bash
python3 -m venv venv
```

### 3) Activate the virtual environment

* **macOS / Linux:** `source venv/bin/activate`
* **Windows (PowerShell):** `venv\Scripts\Activate.ps1`

### 4) Upgrade packaging tools

```bash
pip install --upgrade pip setuptools wheel
```

### 5) Install project dependencies

```bash
pip install -r requirements.txt
```

### 6) Install as CLI (editable mode, optional)

```bash
pip install -e .
```

* Creates `ao3` command for your environment.
* You can also run without installing using `python -m ao3.cli`.

### 7) Verify installation

```bash
# inside venv
which ao3   # should show path to ao3 script
ao3 --help  # should print CLI usage
```

---

## Run examples

### Search

```bash
# module runner
python -m ao3.cli search "Zoro Sanji" --sort kudos --complete --rating M
# or installed CLI
ao3 search "Zoro Sanji" --sort kudos --complete --rating M
```

### Read a fic

```bash
python -m ao3.cli read "https://archiveofourown.org/works/12345678"
ao3 read "https://archiveofourown.org/works/12345678"
```

### Bookmark / List bookmarks

```bash
ao3 bookmark "https://archiveofourown.org/works/12345678" "My Fic Title"
ao3 bookmarks
```

---

## VS Code integration (recommended)

1. Open project in VS Code.
2. `Cmd+Shift+P` → `Python: Select Interpreter` → choose your venv.
3. Reload window if necessary. Pylance will now detect all packages.

Optional `.vscode/settings.json`:

```json
{
  "python.pythonPath": "${workspaceFolder}/venv/bin/python"
}
```

---

## Troubleshooting

* **Pylance: `Import "setuptools" could not be resolved`** → `pip install --upgrade setuptools`
* **AO3 returns 403/429** → Respect AO3 rate limits; use delays between requests.
* **`ao3` command not found** → Ensure venv is active or use `python -m ao3.cli`.

---

## .gitignore

```
venv/
__pycache__/
*.pyc
bookmarks.db
```

---

## Disclaimer

This tool uses HTML scraping to access AO3 and is **not an official API**. Follow AO3 terms of service and rate limits.