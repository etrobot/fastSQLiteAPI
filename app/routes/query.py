from fastapi import APIRouter, Depends, HTTPException
from ..models import QueryBody, CookieRecord, CookieUpdate
from ..database import get_db
from ..config import get_settings
import sqlite3

router = APIRouter()
settings = get_settings()

@router.post("/query")
async def execute_query(body: QueryBody):
    query = body.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query parameter is required")
    
    try:
        async with get_db(settings.db_path) as db:
            is_select = query.upper().startswith('SELECT')
            
            if is_select:
                cursor = await db.execute(query)
                rows = await cursor.fetchall()
                return {"results": [dict(row) for row in rows]}
            else:
                await db.execute(query)
                await db.commit()
                return {
                    "message": "Query executed successfully",
                    "changes": db.total_changes
                }
    except sqlite3.Error as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/cookies")
async def create_cookie(cookie: CookieRecord):
    try:
        async with get_db(settings.db_path) as db:
            cursor = await db.execute('''
                INSERT INTO cookies (domain, cookie, user, updated_at)
                VALUES (?, ?, ?, datetime('now'))
                ON CONFLICT(domain, user) 
                DO UPDATE SET 
                    cookie = excluded.cookie,
                    updated_at = datetime('now')
            ''', (cookie.domain, cookie.cookie, cookie.user))
            await db.commit()
            
            return {
                "message": "Cookie record created/updated successfully",
                "id": cursor.lastrowid
            }
    except sqlite3.Error as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/cookies/{domain}/{user}")
async def get_cookie(domain: str, user: str):
    async with get_db(settings.db_path) as db:
        cursor = await db.execute(
            "SELECT * FROM cookies WHERE domain = ? AND user = ?",
            (domain, user)
        )
        row = await cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Cookie record not found")
        
        return dict(row)

@router.put("/cookies/{domain}/{user}")
async def update_cookie(domain: str, user: str, cookie: CookieUpdate):
    try:
        async with get_db(settings.db_path) as db:
            cursor = await db.execute('''
                UPDATE cookies 
                SET cookie = ?, 
                    updated_at = datetime('now')
                WHERE domain = ? AND user = ?
            ''', (cookie.cookie, domain, user))
            await db.commit()
            
            if cursor.rowcount == 0:
                cursor = await db.execute('''
                    INSERT INTO cookies (domain, cookie, user, updated_at)
                    VALUES (?, ?, ?, datetime('now'))
                ''', (domain, cookie.cookie, user))
                await db.commit()
                
                return {
                    "message": "Cookie record created successfully",
                    "id": cursor.lastrowid
                }
            
            return {
                "message": "Cookie record updated successfully",
                "changes": cursor.rowcount
            }
    except sqlite3.Error as e:
        raise HTTPException(status_code=400, detail=str(e)) 