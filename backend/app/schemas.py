from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class InterfaceInfoBase(BaseModel):
    interface_name: str
    interface_path: str
    parent_id: Optional[int] = None
    jump_rule: Optional[str] = None
    status: int = 1
    creator: str = "system"


class InterfaceInfoCreate(InterfaceInfoBase):
    pass


class InterfaceInfoUpdate(BaseModel):
    interface_name: Optional[str] = None
    interface_path: Optional[str] = None
    parent_id: Optional[int] = None
    jump_rule: Optional[str] = None
    status: Optional[int] = None


class InterfaceInfoResponse(InterfaceInfoBase):
    id: int
    create_time: datetime
    update_time: datetime
    
    class Config:
        from_attributes = True


class TextElementBase(BaseModel):
    interface_id: int
    element_path: str
    text_content: str
    element_type: str
    collect_status: int = 1


class TextElementCreate(TextElementBase):
    pass


class TextElementResponse(TextElementBase):
    id: int
    collect_time: datetime
    
    class Config:
        from_attributes = True


class SpellRuleBase(BaseModel):
    word: str
    word_type: str = "common"
    is_whitelist: int = 0
    remark: Optional[str] = None
    language: str = "en"


class SpellRuleCreate(SpellRuleBase):
    pass


class SpellRuleUpdate(BaseModel):
    word: Optional[str] = None
    word_type: Optional[str] = None
    is_whitelist: Optional[int] = None
    remark: Optional[str] = None
    language: Optional[str] = None


class SpellRuleResponse(SpellRuleBase):
    id: int
    create_time: datetime
    update_time: datetime
    
    class Config:
        from_attributes = True


class SpellErrorBase(BaseModel):
    element_id: int
    error_text: str
    correct_suggest: Optional[str] = None
    error_type: str
    severity_level: int = 2
    is_fixed: int = 0


class SpellErrorCreate(SpellErrorBase):
    pass


class SpellErrorResponse(SpellErrorBase):
    id: int
    check_time: datetime
    fixed_time: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class CheckTaskBase(BaseModel):
    task_name: str
    check_scope: str = "all"
    executor: str = "system"


class CheckTaskCreate(CheckTaskBase):
    pass


class CheckTaskUpdate(BaseModel):
    task_status: Optional[int] = None
    error_count: Optional[int] = None
    report_path: Optional[str] = None
    error_msg: Optional[str] = None


class CheckTaskResponse(CheckTaskBase):
    id: int
    task_status: int
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error_count: int
    report_path: Optional[str] = None
    error_msg: Optional[str] = None
    
    class Config:
        from_attributes = True


class UserBase(BaseModel):
    username: str
    role_id: int = 3


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    status: int
    create_time: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class CrawlConfig(BaseModel):
    base_url: str
    username: Optional[str] = None
    password: Optional[str] = None
    interfaces: List[dict]
    timeout: int = 30


class ReportConfig(BaseModel):
    task_id: int
    format: str = "html"
    include_fixed: bool = False
