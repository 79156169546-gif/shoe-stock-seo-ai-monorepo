import os
import shutil
import json
import sqlite3

APP_DIR = os.path.dirname(os.path.abspath(__file__))
BRAIN_DIR = r"C:\Users\79156\.gemini\antigravity\brain\a7a03cfa-3cc5-48b8-bfbb-d7dd0d49eb15"
DB_PATH = os.path.join(APP_DIR, "stock.db")

# 1. Copy cover
cover_src = os.path.join(BRAIN_DIR, "avito_premium_card_boots_infographic_fixed.jpg")
cover_dst = os.path.join(APP_DIR, "static", "covers", "cover_SHOE-001.jpg")
if os.path.exists(cover_src):
    shutil.copy2(cover_src, cover_dst)

# 2. Seed first item
from database import init_db

init_db()
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("DELETE FROM items WHERE sku = 'SHOE-001'")
cursor.execute("""
INSERT INTO items (
    sku, title, brand, shoe_type, season, gender, size, color, 
    material_upper, heel_height, condition, price_retail, price_fast, price_max, price_target,
    description, cover_photo, photos, status
) VALUES (
    'SHOE-001',
    'Ботильоны Caprice новые натуральная кожа 38',
    'Caprice',
    'Ботильоны',
    'Демисезон 🍂',
    'Женская',
    '38',
    'Черный',
    '100% натуральная кожа',
    '5 см',
    'Новые с биркой',
    13900,
    5200,
    7500,
    7200,
    'Абсолютно новые женские ботильоны / полусапожки премиального немецкого бренда Caprice.\nОригинал, с фабричными бирками и упаковочными вставками. Не носились, в идеальном магазинном состоянии!\n\n✨ ПОЧЕМУ ЭТО ВЫГОДНАЯ ПОКУПКА:\n— 100% натуральная кожа (телячья кожа глубокого черного цвета, мягкая и долговечная).\n— Немецкая колодка Caprice: комфортная поддержка стопы, ноги не устают.\n— Устойчивый широкий каблук (~5 см).\n— Внутренняя молния + эластичная вставка челси.\n— Практичная нескользящая подошва.\n\n📦 ДОСТАВКА И ПРИМЕРКА:\nОтправляю Авито Доставкой в день заказа.',
    '/static/covers/cover_SHOE-001.jpg',
    '["/static/covers/cover_SHOE-001.jpg"]',
    'ready'
)
""")
conn.commit()
conn.close()
print("Seeded item SHOE-001 successfully!")
