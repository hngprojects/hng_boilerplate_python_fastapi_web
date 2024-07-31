from fastapi import APIRouter
from api.v1.routes.auth import auth
from api.v1.routes.newsletter import newsletter
from api.v1.routes.user import user
from api.v1.routes.product import product
from api.v1.routes.notification import notification
from api.v1.routes.testimonial import testimonial
from api.v1.routes.facebook_login import fb_auth
from api.v1.routes.blog import blog
from api.v1.routes.waitlist import waitlist as waitlist_router
from api.v1.routes.billing_plan import bill_plan
from api.v1.routes.google_login import google_auth
from api.v1.routes.invitations import invites
from api.v1.routes.profiles import profile
from api.v1.routes.jobs import jobs
from api.v1.routes.payment import payment
from api.v1.routes.organization import organization
from api.v1.routes.request_password import pwd_reset
from api.v1.routes.activity_logs import activity_logs
from api.v1.routes.contact_us import contact_us
from api.v1.routes.comment import comment
from api.v1.routes.sms_twilio import sms
from api.v1.routes.faq import faq
from tests.run_all_test import test_router
from api.v1.routes.topic import topic
from api.v1.routes.notification_settings import notification_setting
from api.v1.routes.api_tests import test_router
from api.v1.routes.squeeze import squeeze


api_version_one = APIRouter(prefix="/api/v1")

api_version_one.include_router(auth)
api_version_one.include_router(google_auth)
api_version_one.include_router(fb_auth)
api_version_one.include_router(pwd_reset)
api_version_one.include_router(user)
api_version_one.include_router(profile)
api_version_one.include_router(organization)
api_version_one.include_router(product)
api_version_one.include_router(payment)
api_version_one.include_router(bill_plan)
api_version_one.include_router(notification)
api_version_one.include_router(notification_setting)
api_version_one.include_router(invites)
api_version_one.include_router(activity_logs)
api_version_one.include_router(blog)
api_version_one.include_router(comment)
api_version_one.include_router(sms)
api_version_one.include_router(jobs)
api_version_one.include_router(test_router)
api_version_one.include_router(faq)
api_version_one.include_router(topic)
api_version_one.include_router(contact_us)
api_version_one.include_router(waitlist_router)
api_version_one.include_router(newsletter)
api_version_one.include_router(testimonial)
api_version_one.include_router(test_router)
api_version_one.include_router(squeeze)
