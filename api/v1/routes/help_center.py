from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from api.db.database import get_db
from api.utils.dependencies import get_current_admin, get_current_user
from api.v1.models.article import Article
from api.v1.schemas.article import Article as ArticleSchema
from api.v1.schemas.article import ArticleUpdate

help_center = APIRouter(prefix="/help-center", tags=["help"])


@help_center.patch("/topics/{article_id}", response_model=ArticleSchema)
def update_article(
    article_id: str,
    article: ArticleUpdate,
    db: Session = Depends(get_db),
    current_admin_user: dict = Depends(get_current_admin),
):
    # Check if the current user is an admin
    try:
        current_admin_user = get_current_admin(current_admin_user)
    except HTTPException as e:
        if e.status_code == status.HTTP_401_UNAUTHORIZED:
            return JSONResponse(
                content={
                    "success": False,
                    "message": "Access denied. No token provided or token is invalid",
                    "status_code": 401,
                },
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
        elif e.status_code == status.HTTP_403_FORBIDDEN:
            return JSONResponse(
                content={
                    "success": False,
                    "message": "Access denied",
                    "status_code": 403,
                },
                status_code=status.HTTP_403_FORBIDDEN,
            )
        raise e

    db_article = db.query(Article).filter(Article.article_id == article_id).first()
    if db_article is None:
        return JSONResponse(
            content={
                "success": False,
                "message": "Article not found",
                "status_code": 404,
            },
            status_code=status.HTTP_404_NOT_FOUND,
        )

    db_article.title = article.title
    db_article.content = article.content
    db_article.author = article.author
    db.commit()
    db.refresh(db_article)

    return JSONResponse(
        content={
            "success": True,
            "data": {
                "id": db_article.article_id,
                "title": db_article.title,
                "content": db_article.content,
                "author": db_article.author,
                "created_at": db_article.created_at.isoformat(),
                "updated_at": db_article.updated_at.isoformat(),
            },
            "status_code": 200,
        },
        status_code=status.HTTP_200_OK,
    )
