from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import sqlite3
import os

app = FastAPI()
DB_PATH = "data/bookmarks.db"

def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS bookmarks (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, url TEXT, category TEXT, emoji TEXT)')
    conn.commit()
    conn.close()

init_db()

@app.get("/", response_class=HTMLResponse)
def index():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, title, url, category, emoji FROM bookmarks')
    rows = c.fetchall()
    conn.close()
    
    cards = ""
    for r in rows:
        cards += f'''
        <div class="card" data-category="{r[3]}">
            <div class="card-icon">{r[4]}</div>
            <div class="card-content">
                <span class="badge">{r[3]}</span>
                <h3>{r[1]}</h3>
                <a href="{r[2]}" target="_blank" class="link">Visitar ↗</a>
            </div>
            <button class="btn-delete" onclick="deleteBm({r[0]})">×</button>
        </div>
        '''

    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Mi Startpage - Dashboard</title>
        <style>
            :root {{
                --bg: #090d16;
                --panel: #111827;
                --panel-hover: #1f2937;
                --accent: #38bdf8;
                --text: #f3f4f6;
                --muted: #9ca3af;
                --border: #374151;
            }}
            * {{ box-sizing: border-box; }}
            body {{
                background: var(--bg);
                color: var(--text);
                font-family: system-ui, -apple-system, sans-serif;
                margin: 0;
                padding: 40px 20px;
            }}
            .container {{ max-width: 1000px; margin: 0 auto; }}
            header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }}
            h1 {{ margin: 0; font-size: 1.8rem; background: linear-gradient(to right, #38bdf8, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
            
            .controls {{ display: flex; gap: 15px; margin-bottom: 30px; flex-wrap: wrap; }}
            input, select {{
                background: var(--panel);
                border: 1px solid var(--border);
                color: var(--text);
                padding: 10px 14px;
                border-radius: 8px;
                font-size: 0.95rem;
                outline: none;
            }}
            input:focus, select:focus {{ border-color: var(--accent); }}
            
            button {{
                background: var(--accent);
                color: #0f172a;
                border: none;
                font-weight: 600;
                padding: 10px 18px;
                border-radius: 8px;
                cursor: pointer;
                transition: opacity 0.2s;
            }}
            button:hover {{ opacity: 0.9; }}

            .grid {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
                gap: 20px;
            }}
            .card {{
                background: var(--panel);
                border: 1px solid var(--border);
                border-radius: 12px;
                padding: 20px;
                display: flex;
                align-items: flex-start;
                gap: 15px;
                position: relative;
                transition: transform 0.2s, background 0.2s, border-color 0.2s;
            }}
            .card:hover {{
                transform: translateY(-3px);
                background: var(--panel-hover);
                border-color: var(--accent);
            }}
            .card-icon {{ font-size: 2rem; }}
            .card-content {{ flex: 1; }}
            .badge {{
                font-size: 0.75rem;
                background: rgba(56, 189, 248, 0.1);
                color: var(--accent);
                padding: 2px 8px;
                border-radius: 4px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            h3 {{ margin: 8px 0 6px 0; font-size: 1.1rem; }}
            .link {{ color: var(--muted); font-size: 0.85rem; text-decoration: none; }}
            .link:hover {{ color: var(--accent); text-decoration: underline; }}
            
            .btn-delete {{
                background: transparent;
                color: #ef4444;
                padding: 2px 6px;
                font-size: 1.2rem;
                position: absolute;
                top: 10px;
                right: 10px;
            }}
            
            .form-box {{
                background: var(--panel);
                border: 1px solid var(--border);
                padding: 20px;
                border-radius: 12px;
                margin-bottom: 30px;
                display: flex;
                gap: 12px;
                flex-wrap: wrap;
            }}
            .form-box input {{ flex: 1; min-width: 150px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>🚀 Mi Startpage</h1>
                <span style="color: var(--muted); font-size: 0.9rem;">Dashboard Personal</span>
            </header>

            <form class="form-box" action="/add" method="POST">
                <input type="text" name="emoji" placeholder="Emoji (ej. 🛠️)" style="max-width: 90px;" required>
                <input type="text" name="title" placeholder="Título" required>
                <input type="url" name="url" placeholder="https://ejemplo.com" required>
                <input type="text" name="category" placeholder="Categoría (ej. Dev)" required>
                <button type="submit">+ Añadir Marcador</button>
            </form>

            <div class="controls">
                <input type="text" id="search" placeholder="🔍 Filtrar marcadores..." oninput="filterCards()" style="flex: 1;">
            </div>

            <div class="grid" id="bookmarkGrid">
                {cards}
            </div>
        </div>

        <script>
            async function deleteBm(id) {{
                if (!confirm("¿Eliminar este marcador?")) return;
                await fetch('/delete/' + id, {{ method: 'DELETE' }});
                location.reload();
            }}

            function filterCards() {{
                const query = document.getElementById('search').value.toLowerCase();
                const cards = document.querySelectorAll('.card');
                cards.forEach(card => {{
                    const text = card.textContent.toLowerCase();
                    card.style.display = text.includes(query) ? 'flex' : 'none';
                }});
            }}
        </script>
    </body>
    </html>
    """

@app.post("/add")
def add(emoji: str = Form(...), title: str = Form(...), url: str = Form(...), category: str = Form(...)):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO bookmarks (title, url, category, emoji) VALUES (?,?,?,?)', (title, url, category, emoji))
    conn.commit()
    conn.close()
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/", status_code=303)

@app.delete("/delete/{bookmark_id}")
def delete_bookmark(bookmark_id: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('DELETE FROM bookmarks WHERE id = ?', (bookmark_id,))
    conn.commit()
    conn.close()
    return { "status": "deleted" }
