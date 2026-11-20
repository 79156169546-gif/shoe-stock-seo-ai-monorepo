import os
import shutil
import json
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from database import init_db, get_all_items, get_item_by_id, create_raw_item, update_item, delete_item, get_stats
from ai_pipeline import analyze_and_enrich_shoe, generate_cover_infographic_concept1 as generate_cover_infographic

app = FastAPI(title="Shoe Stock & Listing Machine")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
UPLOADS_DIR = os.path.join(STATIC_DIR, "uploads")
COVERS_DIR = os.path.join(STATIC_DIR, "covers")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

# Ensure dirs exist
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(COVERS_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

init_db()

@app.get("/", response_class=FileResponse)
async def index_page():
    return FileResponse(os.path.join(TEMPLATES_DIR, "index.html"))

@app.get("/api/stats")
async def api_stats():
    return get_stats()

@app.get("/api/items")
async def api_get_items(status: Optional[str] = None, season: Optional[str] = None, search: Optional[str] = None):
    items = get_all_items(status=status, season=season, search=search)
    return items

@app.get("/api/items/{item_id}")
async def api_get_item(item_id: int):
    item = get_item_by_id(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.post("/api/items/raw")
async def api_create_raw_item(
    notes: Optional[str] = Form(""),
    size: Optional[str] = Form("38"),
    files: List[UploadFile] = File(...)
):
    saved_photos = []
    for file in files:
        if file.filename:
            filename = f"{os.urandom(4).hex()}_{file.filename}"
            filepath = os.path.join(UPLOADS_DIR, filename)
            with open(filepath, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            saved_photos.append(f"/static/uploads/{filename}")
            
    item_id = create_raw_item(saved_photos, notes=notes, custom_size=size)
    return {"status": "success", "item_id": item_id}

@app.post("/api/items/{item_id}/process")
async def api_process_item(item_id: int):
    item = get_item_by_id(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
        
    # 1. Run AI analysis & enrichment
    enriched = analyze_and_enrich_shoe(item)
    
    # 2. Generate Infographic Cover if there are photos
    cover_url = item.get("cover_photo")
    if item["photos"] and len(item["photos"]) > 0:
        first_photo_rel = item["photos"][0].replace("/static/", "")
        first_photo_path = os.path.join(STATIC_DIR, first_photo_rel)
        
        gen_cover = generate_cover_infographic(
            input_photo_path=first_photo_path,
            brand=enriched["brand"],
            shoe_type=enriched["shoe_type"],
            material=enriched["material_upper"],
            heel=enriched["heel_height"],
            size=enriched["size"],
            sku=item["sku"]
        )
        if gen_cover:
            cover_url = gen_cover
            
    enriched["cover_photo"] = cover_url
    update_item(item_id, enriched)
    return {"status": "success", "item": get_item_by_id(item_id)}

@app.post("/api/items/{item_id}/verify-link")
async def api_verify_link(item_id: int, request: Request):
    data = await request.json()
    link_id = data.get("link_id")
    action = data.get("action") # "confirm" or "reject"
    
    item = get_item_by_id(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
        
    links = item.get("reference_links", [])
    for lnk in links:
        if lnk.get("id") == link_id:
            lnk["status"] = "confirmed" if action == "confirm" else "rejected"
            break
            
    update_item(item_id, {"reference_links": links})
    return {"status": "success", "reference_links": links}

@app.post("/api/items/{item_id}/regenerate-photos")
async def api_regenerate_photos(item_id: int):
    item = get_item_by_id(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
        
    if not item["photos"] or len(item["photos"]) == 0:
        raise HTTPException(status_code=400, detail="No photos to regenerate from")
        
    first_photo_rel = item["photos"][0].replace("/static/", "")
    first_photo_path = os.path.join(STATIC_DIR, first_photo_rel)
    
    new_cover = generate_cover_infographic(
        input_photo_path=first_photo_path,
        brand=item.get("brand", "Caprice"),
        shoe_type=item.get("shoe_type", "Ботильоны"),
        material=item.get("material_upper", "100% натуральная кожа"),
        heel=item.get("heel_height", "5 см"),
        size=item.get("size", "38"),
        sku=item.get("sku", "SHOE")
    )
    
    catalog_photos = [new_cover] if new_cover else []
    # If other photos exist, keep them in catalog photos
    for p in item["photos"][1:]:
        catalog_photos.append(p)
        
    update_item(item_id, {
        "cover_photo": new_cover,
        "catalog_photos": catalog_photos
    })
    return {"status": "success", "item": get_item_by_id(item_id)}

@app.post("/api/items/{item_id}/update")
async def api_update_item(item_id: int, request: Request):
    data = await request.json()
    update_item(item_id, data)
    return {"status": "success", "item": get_item_by_id(item_id)}

@app.post("/api/items/{item_id}/delete")
async def api_delete_item(item_id: int):
    delete_item(item_id)
    return {"status": "success"}

@app.get("/api/export/avito")
async def api_export_avito():
    items = get_all_items(status="ready")
    if not items:
        items = get_all_items() # fallback to all
        
    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<Ads formatVersion="3" target="Avito.ru">'
    ]
    for it in items:
        xml_lines.append(f'  <Ad>')
        xml_lines.append(f'    <Id>{it["sku"]}</Id>')
        xml_lines.append(f'    <Category>Одежда, обувь, аксессуары</Category>')
        xml_lines.append(f'    <GoodsSubType>Женская обувь</GoodsSubType>')
        xml_lines.append(f'    <Apparel>{it["shoe_type"]}</Apparel>')
        xml_lines.append(f'    <Title><![CDATA[{it["title"]}]]></Title>')
        xml_lines.append(f'    <Description><![CDATA[{it["description"]}]]></Description>')
        xml_lines.append(f'    <Price>{it["price_target"]}</Price>')
        xml_lines.append(f'    <Size>{it["size"]}</Size>')
        xml_lines.append(f'    <Condition>Новое с биркой</Condition>')
        xml_lines.append(f'    <Color>{it["color"]}</Color>')
        xml_lines.append(f'    <Brand>{it["brand"]}</Brand>')
        xml_lines.append(f'  </Ad>')
    xml_lines.append('</Ads>')
    
    export_path = os.path.join(BASE_DIR, "avito_feed.xml")
    with open(export_path, "w", encoding="utf-8") as f:
        f.write("\n".join(xml_lines))
        
    return FileResponse(export_path, media_type="application/xml", filename="avito_feed.xml")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8765, reload=False)
