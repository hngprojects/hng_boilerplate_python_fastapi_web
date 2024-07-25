from fastapi import APIRouter
from api.v1.routes.auth import auth
from api.v1.routes.newsletter import newsletter
from api.v1.routes.user import user
from api.v1.routes.superadmin import superadmin
from api.v1.routes.product import product
from api.v1.routes.notification import notification
from api.v1.routes.testimonial import testimonial
from api.v1.routes.facebook_login import fb_auth
from api.v1.routes.blog import blog
from api.v1.routes.waitlist import waitlist

api_version_one = APIRouter(prefix="/api/v1")

api_version_one.include_router(auth)
api_version_one.include_router(newsletter)
api_version_one.include_router(user)
api_version_one.include_router(product)
api_version_one.include_router(notification)
api_version_one.include_router(testimonial)
api_version_one.include_router(fb_auth)
api_version_one.include_router(blog)
api_version_one.include_router(waitlist)
api_version_one.include_router(superadmin)

