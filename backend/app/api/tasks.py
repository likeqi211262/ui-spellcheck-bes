from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.api.auth import get_current_user
from app.core.spell_checker import SpellCheckEngine
from app.core.crawler import WebCrawler
from app.core.report_generator import ReportGenerator

router = APIRouter(prefix="/tasks", tags=["check-tasks"])


def execute_check_task(task_id: int, db_url: str):
    from app.database import SessionLocal
    db = SessionLocal()
    
    try:
        task = db.query(models.CheckTask).filter(models.CheckTask.id == task_id).first()
        if not task:
            return
        
        task.task_status = 1
        task.start_time = datetime.now()
        db.commit()
        
        if task.check_scope == "all":
            interfaces = db.query(models.InterfaceInfo).filter(
                models.InterfaceInfo.status == 1
            ).all()
        else:
            interface_ids = [int(x) for x in task.check_scope.split(",") if x.strip()]
            interfaces = db.query(models.InterfaceInfo).filter(
                models.InterfaceInfo.id.in_(interface_ids)
            ).all()
        
        crawler = WebCrawler(db, headless=True)
        spell_checker = SpellCheckEngine(db)
        
        try:
            crawler.init_driver()
            
            total_errors = 0
            for interface in interfaces:
                try:
                    text_elements, screenshot_path = crawler.crawl_interface(
                        interface.id, 
                        interface.interface_path,
                        task_id
                    )
                    
                    if screenshot_path:
                        interface.screenshot_path = screenshot_path
                        db.commit()
                    
                    for text_data in text_elements:
                        text_element = models.TextElement(
                            interface_id=interface.id,
                            element_path=text_data['path'],
                            text_content=text_data['text'],
                            element_type=text_data['type'],
                            collect_status=1
                        )
                        db.add(text_element)
                        db.commit()
                        db.refresh(text_element)
                        
                        errors = spell_checker.check_text(text_data['text'])
                        
                        for error in errors:
                            spell_error = models.SpellError(
                                element_id=text_element.id,
                                error_text=error['error_text'],
                                correct_suggest=error['correct_suggest'],
                                error_type=error['error_type'],
                                severity_level=error['severity_level'],
                                is_fixed=0
                            )
                            db.add(spell_error)
                            total_errors += 1
                    
                    db.commit()
                except Exception as e:
                    print(f"Error processing interface {interface.interface_name}: {str(e)}")
                    continue
        finally:
            crawler.close_driver()
        
        task.task_status = 2
        task.end_time = datetime.now()
        task.error_count = total_errors
        db.commit()
        
    except Exception as e:
        task.task_status = 3
        task.end_time = datetime.now()
        task.error_msg = str(e)
        db.commit()
    finally:
        db.close()


@router.get("/", response_model=List[schemas.CheckTaskResponse])
async def get_tasks(
    skip: int = 0,
    limit: int = 100,
    status: int = None,
    db: Session = Depends(get_db),
    current_user: models.SysUser = Depends(get_current_user)
):
    query = db.query(models.CheckTask)
    
    if status is not None:
        query = query.filter(models.CheckTask.task_status == status)
    
    tasks = query.order_by(models.CheckTask.create_time.desc()).offset(skip).limit(limit).all()
    return tasks


@router.post("/", response_model=schemas.CheckTaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task: schemas.CheckTaskCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: models.SysUser = Depends(get_current_user)
):
    db_task = models.CheckTask(**task.model_dump(), task_status=0)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    from app.config import get_settings
    settings = get_settings()
    background_tasks.add_task(execute_check_task, db_task.id, settings.DATABASE_URL)
    
    return db_task


@router.get("/{task_id}", response_model=schemas.CheckTaskResponse)
async def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: models.SysUser = Depends(get_current_user)
):
    db_task = db.query(models.CheckTask).filter(models.CheckTask.id == task_id).first()
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    return db_task


@router.post("/{task_id}/generate-report")
async def generate_report(
    task_id: int,
    format: str = "html",
    include_fixed: bool = False,
    db: Session = Depends(get_db),
    current_user: models.SysUser = Depends(get_current_user)
):
    db_task = db.query(models.CheckTask).filter(models.CheckTask.id == task_id).first()
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    if db_task.task_status != 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task is not completed yet"
        )
    
    report_gen = ReportGenerator(db)
    
    if format == "html":
        filepath = report_gen.generate_html_report(task_id, include_fixed)
    elif format == "excel":
        filepath = report_gen.generate_excel_report(task_id, include_fixed)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported report format"
        )
    
    return {"report_path": filepath}


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: models.SysUser = Depends(get_current_user)
):
    db_task = db.query(models.CheckTask).filter(models.CheckTask.id == task_id).first()
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    db.delete(db_task)
    db.commit()
    
    return None
