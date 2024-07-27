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
from api.v1.routes.waitlist import waitlist as waitlist_router
from api.v1.routes.billing_plan import bill_plan
from api.v1.routes.google_login import google_auth
from api.v1.routes.notifications import notifications
from api.v1.routes.invitations import invites
from api.v1.routes.profiles import profile
from api.v1.routes.job import job

api_version_one = APIRouter(prefix="/api/v1")

api_version_one.include_router(auth)
api_version_one.include_router(newsletter)
api_version_one.include_router(user)
api_version_one.include_router(superadmin)
api_version_one.include_router(notifications)
api_version_one.include_router(product)
api_version_one.include_router(notification)
api_version_one.include_router(testimonial)
api_version_one.include_router(fb_auth)
api_version_one.include_router(blog)
api_version_one.include_router(waitlist_router)
api_version_one.include_router(bill_plan)
api_version_one.include_router(google_auth)
api_version_one.include_router(invites)
api_version_one.include_router(profile)
api_version_one.include_router(job) 

