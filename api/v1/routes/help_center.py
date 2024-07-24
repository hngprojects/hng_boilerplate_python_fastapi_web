from api.db.database import get_db
from api.utils.dependencies import get_super_admin
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from api.v1.models.blog import Blog
from api.v1.schemas.blog import BlogResponse


router = APIRouter(prefix="/help-center", tags=["Help center"])

@router.patch("/topics/{blog_id}", response_model=BlogResponse)
def update_article(
    blog_id: str,
    article: ArticleUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_super_admin)
):
    # Check if the current user is an admin
    try:
        current_user = get_super_admin(current_user)
    except HTTPException as e:
        if e.status_code == status.HTTP_401_UNAUTHORIZED:
            return JSONResponse(
                content={
                    "success": False,
                    "message": "Access denied. No token provided or token is invalid",
                    "status_code": 401
                },
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        elif e.status_code == status.HTTP_403_FORBIDDEN:
            return JSONResponse(
                content={
                    "success": False,
                    "message": "Access denied",
                    "status_code": 403
                },
                status_code=status.HTTP_403_FORBIDDEN
            )
        raise e

    # Check if artile exist
    db_blog = db.query(Blog).filter(Blog.blog_id == blog_id).first()
    if db_blog is None:
        return JSONResponse(
            content={
                "success": False,
                "message": "Article not found",
                "status_code": 404
            },
            status_code=status.HTTP_404_NOT_FOUND
        )

    db_blog.title = article.title
    db_blog.content = article.content
    db_blog.author = article.author
    db.commit()
    db.refresh(db_blog)

    return JSONResponse(
        content={
            "success": True,
            "data": {
                "id": db_blog.blog_id,
                "title": db_blog.title,
                "content": db_blog.content,
                "author": db_blog.author,
                "created_at": db_blog.created_at.isoformat(),
                "updated_at": db_blog.updated_at.isoformat()
            },
            "status_code": 200
        },
        status_code=status.HTTP_200_OK
    )

@router.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    if exc.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY:
        return JSONResponse(
            content={
                "success": False,
                "message": "Invalid input data",
                "status_code": 422
            },
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )
    # Handle other exceptions if needed
    return JSONResponse(
        content={
            "success": False,
            "message": "An error occurred",
            "status_code": exc.status_code
        },
        status_code=exc.status_code
    )
