import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "stock.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sku TEXT UNIQUE,
        title TEXT,
        brand TEXT,
        shoe_type TEXT,
        season TEXT,
        gender TEXT DEFAULT 'Женская',
        size TEXT,
        color TEXT DEFAULT 'Черный',
        material_upper TEXT DEFAULT 'Натуральная кожа',
        material_inner TEXT DEFAULT 'Текстиль / Байка',
        heel_height TEXT DEFAULT '5 см',
        condition TEXT DEFAULT 'Новые с биркой',
        price_retail INTEGER DEFAULT 12000,
        price_fast INTEGER DEFAULT 5000,
        price_max INTEGER DEFAULT 7500,
        price_target INTEGER DEFAULT 7200,
        cost_price INTEGER DEFAULT 0,
        description TEXT,
        cover_photo TEXT,
        photos TEXT, -- JSON array of original file paths
        catalog_photos TEXT, -- JSON array of generated studio photos
        reference_links TEXT, -- JSON array of found links: [{url, title, status}]
        status TEXT DEFAULT 'raw', -- 'raw', 'ready', 'active', 'sold'
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()

def get_all_items(status=None, season=None, search=None):
    conn = get_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM items WHERE 1=1"
    params = []
    
    if status:
        query += " AND status = ?"
        params.append(status)
    if season:
        query += " AND season LIKE ?"
        params.append(f"%{season}%")
    if search:
        query += " AND (title LIKE ? OR brand LIKE ? OR sku LIKE ? OR size LIKE ?)"
        term = f"%{search}%"
        params.extend([term, term, term, term])
        
    query += " ORDER BY id DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    items = []
    for r in rows:
        d = dict(r)
        d["photos"] = json.loads(d["photos"]) if d.get("photos") else []
        d["catalog_photos"] = json.loads(d["catalog_photos"]) if d.get("catalog_photos") else []
        d["reference_links"] = json.loads(d["reference_links"]) if d.get("reference_links") else []
        items.append(d)
    return items

def get_item_by_id(item_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items WHERE id = ?", (item_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        d = dict(row)
        d["photos"] = json.loads(d["photos"]) if d.get("photos") else []
        d["catalog_photos"] = json.loads(d["catalog_photos"]) if d.get("catalog_photos") else []
        d["reference_links"] = json.loads(d["reference_links"]) if d.get("reference_links") else []
        return d
    return None

def create_raw_item(photos, notes="", custom_size=""):
    conn = get_connection()
    cursor = conn.cursor()
    
    # Generate next SKU
    cursor.execute("SELECT COUNT(*) FROM items")
    count = cursor.fetchone()[0] + 1
    sku = f"SHOE-{count:03d}"
    
    cursor.execute("""
    INSERT INTO items (sku, title, brand, shoe_type, season, size, photos, status, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?, 'raw', ?)
    """, (
        sku,
        f"Позиция {sku} (Сырая)",
        "Не определен",
        "Обувь",
        "Демисезон 🍂",
        custom_size if custom_size else "38",
        json.dumps(photos),
        notes
    ))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return new_id

def update_item(item_id, update_data):
    conn = get_connection()
    cursor = conn.cursor()
    
    fields = []
    values = []
    for k, v in update_data.items():
        if k in ["photos", "catalog_photos", "reference_links"] and isinstance(v, list):
            v = json.dumps(v, ensure_ascii=False)
        fields.append(f"{k} = ?")
        values.append(v)
        
    fields.append("updated_at = CURRENT_TIMESTAMP")
    values.append(item_id)
    
    query = f"UPDATE items SET {', '.join(fields)} WHERE id = ?"
    cursor.execute(query, values)
    conn.commit()
    conn.close()

def delete_item(item_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM items WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()

def get_stats():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN status = 'raw' THEN 1 ELSE 0 END) as raw_count,
        SUM(CASE WHEN status = 'ready' THEN 1 ELSE 0 END) as ready_count,
        SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active_count,
        SUM(CASE WHEN status = 'sold' THEN 1 ELSE 0 END) as sold_count,
        SUM(CASE WHEN status != 'sold' THEN price_target ELSE 0 END) as total_stock_value,
        SUM(CASE WHEN status = 'sold' THEN price_target ELSE 0 END) as total_revenue
    FROM items
    """)
    row = cursor.fetchone()
    conn.close()
    return dict(row)

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully at:", DB_PATH)
