from fastapi import APIRouter, Query, HTTPException
from fastapi import Depends

from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from api.core import responses
from api.db.database import get_db
from api.v1.models.articles import Article
from api.v1.schemas.articles import ArticleResponse, SearchResponse

app = APIRouter()


@app.get("/api/v1/topics/search", response_model=SearchResponse)
async def search_articles(
    title: str = Query(..., min_length=1), db: Session = Depends(get_db)
):
    try:
        articles = db.query(Article).filter(Article.title.ilike(f"%{title}%")).all()
        if not articles:
            raise HTTPException(
                status_code=404, detail="No article matches the title search param."
            )
        topics = [
            ArticleResponse(
                article_id=article.article_id,
                title=article.title,
                content=article.content,
            )
            for article in articles
        ]
        return SearchResponse(
            success=True, message="Articles found", status_code=200, topics=topics
        )
    except HTTPException as exc:
        if exc.status_code == 404:
            return JSONResponse(
                status_code=404,
                content={"success": False, "message": responses.NOT_FOUND, "status_code": 404},
            )
        elif exc.status_code == 429:
            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "message": responses.TOO_MANY_REQUEST,
                    "status_code": 429,
                },
            )
        elif exc.status_code == 500:
            return JSONResponse(
                status_code=500,
                content={"success": False, "message": responses.SERVER_ERROR, "status_code": 500},
            )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "message": exc.detail,
                "status_code": exc.status_code,
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=responses.SERVER_ERROR)
