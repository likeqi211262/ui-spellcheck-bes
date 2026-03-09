from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.api.auth import get_current_user

router = APIRouter(prefix="/interfaces", tags=["interfaces"])


@router.get("/", response_model=List[schemas.InterfaceInfoResponse])
async def get_interfaces(
    skip: int = 0,
    limit: int = 100,
    status: int = None,
    db: Session = Depends(get_db),
    current_user: models.SysUser = Depends(get_current_user)
):
    query = db.query(models.InterfaceInfo)
    
    if status is not None:
        query = query.filter(models.InterfaceInfo.status == status)
    
    interfaces = query.offset(skip).limit(limit).all()
    return interfaces


@router.post("/", response_model=schemas.InterfaceInfoResponse, status_code=status.HTTP_201_CREATED)
async def create_interface(
    interface: schemas.InterfaceInfoCreate,
    db: Session = Depends(get_db),
    current_user: models.SysUser = Depends(get_current_user)
):
    db_interface = models.InterfaceInfo(**interface.model_dump())
    db.add(db_interface)
    db.commit()
    db.refresh(db_interface)
    
    return db_interface


@router.put("/{interface_id}", response_model=schemas.InterfaceInfoResponse)
async def update_interface(
    interface_id: int,
    interface: schemas.InterfaceInfoUpdate,
    db: Session = Depends(get_db),
    current_user: models.SysUser = Depends(get_current_user)
):
    db_interface = db.query(models.InterfaceInfo).filter(
        models.InterfaceInfo.id == interface_id
    ).first()
    
    if not db_interface:
        raise HTTPException(status_code=404, detail="Interface not found")
    
    update_data = interface.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_interface, key, value)
    
    db.commit()
    db.refresh(db_interface)
    
    return db_interface


@router.delete("/{interface_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_interface(
    interface_id: int,
    db: Session = Depends(get_db),
    current_user: models.SysUser = Depends(get_current_user)
):
    db_interface = db.query(models.InterfaceInfo).filter(
        models.InterfaceInfo.id == interface_id
    ).first()
    
    if not db_interface:
        raise HTTPException(status_code=404, detail="Interface not found")
    
    db.delete(db_interface)
    db.commit()
    
    return None


@router.get("/{interface_id}", response_model=schemas.InterfaceInfoResponse)
async def get_interface(
    interface_id: int,
    db: Session = Depends(get_db),
    current_user: models.SysUser = Depends(get_current_user)
):
    db_interface = db.query(models.InterfaceInfo).filter(
        models.InterfaceInfo.id == interface_id
    ).first()
    
    if not db_interface:
        raise HTTPException(status_code=404, detail="Interface not found")
    
    return db_interface


@router.get("/{interface_id}/texts", response_model=List[schemas.TextElementResponse])
async def get_interface_texts(
    interface_id: int,
    db: Session = Depends(get_db),
    current_user: models.SysUser = Depends(get_current_user)
):
    texts = db.query(models.TextElement).filter(
        models.TextElement.interface_id == interface_id
    ).all()
    
    return texts
