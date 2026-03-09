from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.api.auth import get_current_user

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/errors", response_model=List[schemas.SpellErrorResponse])
async def get_errors(
    skip: int = 0,
    limit: int = 100,
    task_id: int = None,
    severity: int = None,
    error_type: str = None,
    is_fixed: int = None,
    db: Session = Depends(get_db),
    current_user: models.SysUser = Depends(get_current_user)
):
    query = db.query(models.SpellError)
    
    if task_id:
        task = db.query(models.CheckTask).filter(models.CheckTask.id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        if task.check_scope == "all":
            interface_ids = [i.id for i in db.query(models.InterfaceInfo).all()]
        else:
            interface_ids = [int(x) for x in task.check_scope.split(",") if x.strip()]
        
        element_ids = db.query(models.TextElement.id).filter(
            models.TextElement.interface_id.in_(interface_ids)
        ).all()
        element_ids = [e[0] for e in element_ids]
        query = query.filter(models.SpellError.element_id.in_(element_ids))
    
    if severity is not None:
        query = query.filter(models.SpellError.severity_level == severity)
    
    if error_type:
        query = query.filter(models.SpellError.error_type == error_type)
    
    if is_fixed is not None:
        query = query.filter(models.SpellError.is_fixed == is_fixed)
    
    errors = query.offset(skip).limit(limit).all()
    return errors


@router.put("/errors/{error_id}/fix", response_model=schemas.SpellErrorResponse)
async def mark_error_fixed(
    error_id: int,
    db: Session = Depends(get_db),
    current_user: models.SysUser = Depends(get_current_user)
):
    from datetime import datetime
    
    error = db.query(models.SpellError).filter(models.SpellError.id == error_id).first()
    if not error:
        raise HTTPException(status_code=404, detail="Error not found")
    
    error.is_fixed = 1
    error.fixed_time = datetime.now()
    db.commit()
    db.refresh(error)
    
    return error


@router.get("/download/{task_id}")
async def download_report(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: models.SysUser = Depends(get_current_user)
):
    task = db.query(models.CheckTask).filter(models.CheckTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if not task.report_path:
        raise HTTPException(status_code=404, detail="Report not generated")
    
    import os
    if not os.path.exists(task.report_path):
        raise HTTPException(status_code=404, detail="Report file not found")
    
    return FileResponse(
        task.report_path,
        media_type='application/octet-stream',
        filename=os.path.basename(task.report_path)
    )


@router.get("/statistics/{task_id}")
async def get_statistics(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: models.SysUser = Depends(get_current_user)
):
    task = db.query(models.CheckTask).filter(models.CheckTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.check_scope == "all":
        interface_ids = [i.id for i in db.query(models.InterfaceInfo).all()]
    else:
        interface_ids = [int(x) for x in task.check_scope.split(",") if x.strip()]
    
    element_ids = db.query(models.TextElement.id).filter(
        models.TextElement.interface_id.in_(interface_ids)
    ).all()
    element_ids = [e[0] for e in element_ids]
    
    query = db.query(models.SpellError).filter(models.SpellError.element_id.in_(element_ids))
    
    total_errors = query.count()
    fixed_errors = query.filter(models.SpellError.is_fixed == 1).count()
    
    from sqlalchemy import func
    by_severity = db.query(
        models.SpellError.severity_level,
        func.count(models.SpellError.id)
    ).filter(
        models.SpellError.element_id.in_(element_ids)
    ).group_by(models.SpellError.severity_level).all()
    
    by_type = db.query(
        models.SpellError.error_type,
        func.count(models.SpellError.id)
    ).filter(
        models.SpellError.element_id.in_(element_ids)
    ).group_by(models.SpellError.error_type).all()
    
    return {
        "total_errors": total_errors,
        "fixed_errors": fixed_errors,
        "unfixed_errors": total_errors - fixed_errors,
        "by_severity": {str(sev): count for sev, count in by_severity},
        "by_type": {err_type: count for err_type, count in by_type}
    }
