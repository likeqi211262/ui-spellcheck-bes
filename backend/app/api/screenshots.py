import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.api.auth import get_current_user

router = APIRouter(prefix="/screenshots", tags=["screenshots"])


@router.get("/{interface_id}")
async def get_screenshot(
    interface_id: int,
    db: Session = Depends(get_db),
    current_user: models.SysUser = Depends(get_current_user)
):
    interface = db.query(models.InterfaceInfo).filter(
        models.InterfaceInfo.id == interface_id
    ).first()
    
    if not interface:
        raise HTTPException(status_code=404, detail="Interface not found")
    
    if not interface.screenshot_path:
        raise HTTPException(status_code=404, detail="Screenshot not available")
    
    if not os.path.exists(interface.screenshot_path):
        raise HTTPException(status_code=404, detail="Screenshot file not found")
    
    return FileResponse(
        interface.screenshot_path,
        media_type='image/png',
        filename=f"screenshot_{interface_id}.png"
    )
