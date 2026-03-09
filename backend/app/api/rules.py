from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.api.auth import get_current_user
from app.core.spell_checker import SpellCheckEngine

router = APIRouter(prefix="/rules", tags=["spell-rules"])


@router.get("/", response_model=List[schemas.SpellRuleResponse])
async def get_rules(
    skip: int = 0,
    limit: int = 100,
    word_type: str = None,
    language: str = None,
    db: Session = Depends(get_db),
    current_user: models.SysUser = Depends(get_current_user)
):
    query = db.query(models.SpellRule)
    
    if word_type:
        query = query.filter(models.SpellRule.word_type == word_type)
    
    if language:
        query = query.filter(models.SpellRule.language == language)
    
    rules = query.offset(skip).limit(limit).all()
    return rules


@router.post("/", response_model=schemas.SpellRuleResponse, status_code=status.HTTP_201_CREATED)
async def create_rule(
    rule: schemas.SpellRuleCreate,
    db: Session = Depends(get_db),
    current_user: models.SysUser = Depends(get_current_user)
):
    db_rule = db.query(models.SpellRule).filter(models.SpellRule.word == rule.word).first()
    if db_rule:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Word already exists in rule database"
        )
    
    db_rule = models.SpellRule(**rule.model_dump())
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    
    engine = SpellCheckEngine(db)
    engine.reload_rules()
    
    return db_rule


@router.put("/{rule_id}", response_model=schemas.SpellRuleResponse)
async def update_rule(
    rule_id: int,
    rule: schemas.SpellRuleUpdate,
    db: Session = Depends(get_db),
    current_user: models.SysUser = Depends(get_current_user)
):
    db_rule = db.query(models.SpellRule).filter(models.SpellRule.id == rule_id).first()
    if not db_rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rule not found"
        )
    
    update_data = rule.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_rule, key, value)
    
    db.commit()
    db.refresh(db_rule)
    
    engine = SpellCheckEngine(db)
    engine.reload_rules()
    
    return db_rule


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: models.SysUser = Depends(get_current_user)
):
    db_rule = db.query(models.SpellRule).filter(models.SpellRule.id == rule_id).first()
    if not db_rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rule not found"
        )
    
    db.delete(db_rule)
    db.commit()
    
    engine = SpellCheckEngine(db)
    engine.reload_rules()
    
    return None


@router.get("/{rule_id}", response_model=schemas.SpellRuleResponse)
async def get_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: models.SysUser = Depends(get_current_user)
):
    db_rule = db.query(models.SpellRule).filter(models.SpellRule.id == rule_id).first()
    if not db_rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rule not found"
        )
    
    return db_rule


@router.post("/batch", status_code=status.HTTP_201_CREATED)
async def batch_create_rules(
    rules: List[schemas.SpellRuleCreate],
    db: Session = Depends(get_db),
    current_user: models.SysUser = Depends(get_current_user)
):
    created_count = 0
    for rule in rules:
        db_rule = db.query(models.SpellRule).filter(models.SpellRule.word == rule.word).first()
        if not db_rule:
            db_rule = models.SpellRule(**rule.model_dump())
            db.add(db_rule)
            created_count += 1
    
    db.commit()
    
    engine = SpellCheckEngine(db)
    engine.reload_rules()
    
    return {"message": f"Successfully created {created_count} rules"}
