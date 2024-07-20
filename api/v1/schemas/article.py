from pydantic import BaseModel


class ArticleResponse(BaseModel):
    article_id: str
    title: str
    content: str


class SearchResponse(BaseModel):
    success: bool
    message: str
    status_code: int
    topics: list[ArticleResponse]