from pydantic import BaseModel, constr
from typing import Optional, List
from datetime import datetime
from enum import Enum

class InteractionType(str, Enum):
    LIKE = "like"
    COMMENT = "comment"
    SHARE = "share"
    FOLLOW = "follow"

class InteractionBase(BaseModel):
    user_id: int
    target_id: int
    interaction_type: InteractionType
    content: Optional[str] = None

class InteractionCreate(InteractionBase):
    pass

class InteractionUpdate(BaseModel):
    content: Optional[str] = None

class InteractionResponse(InteractionBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class InteractionList(BaseModel):
    interactions: List[InteractionResponse]
    total: int
    page: int
    per_page: int

class CommentCreate(BaseModel):
    content: constr(min_length=1, max_length=1000)
    user_id: int
    target_id: int

class CommentResponse(CommentCreate):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True 