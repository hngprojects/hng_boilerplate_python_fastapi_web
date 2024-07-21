from fastapi import APIRouter
from api.v1.routes.auth import auth
from api.v1.routes.roles import role
from api.v1.routes.blog import blogs
from api.v1.routes.plans import plans
from api.v1.routes.blog import blogs
from api.v1.routes.blog import blogs
from api.v1.routes.newsletter_router import newsletter

api_version_one = APIRouter(prefix="/api/v1")

api_version_one.include_router(auth)
api_version_one.include_router(role)
api_version_one.include_router(newsletter)
api_version_one.include_router(blogs)
api_version_one.include_router(plans)
api_version_one.include_router(blogs)
