from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ArticleBase(BaseModel):
    title: str
    content: str


class ArticleUpdate(ArticleBase):
    pass

class Article(ArticleBase):
    article_id: str
    createdAt: Optional[datetime]
    updatedAt: Optional[datetime]

    class Config:
        orm_mode = True
