from api.v1.routes.settings import settings
from api.v1.routes.privacy import privacies
from api.v1.routes.team import team
from fastapi import APIRouter
from api.v1.routes.api_status import api_status
from api.v1.routes.auth import auth
from api.v1.routes.faq_inquiries import faq_inquiries
from api.v1.routes.newsletter import newsletter, news_sub
from api.v1.routes.user import user_router
from api.v1.routes.product import product, non_organisation_product
from api.v1.routes.product_comment import product_comment
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
from api.v1.routes.organisation import organisation
from api.v1.routes.request_password import pwd_reset
from api.v1.routes.activity_logs import activity_logs
from api.v1.routes.contact_us import contact_us
from api.v1.routes.comment import comment
from api.v1.routes.sms_twilio import sms
from api.v1.routes.faq import faq
import api.v1.routes.payment_flutterwave
from tests.run_all_test import test_rout
from api.v1.routes.topic import topic
from api.v1.routes.notification_settings import notification_setting
from api.v1.routes.regions import regions
from api.v1.routes.api_tests import test_router
from api.v1.routes.email_routes import email_sender
from api.v1.routes.squeeze import squeeze
from api.v1.routes.dashboard import dashboard
from api.v1.routes.email_template import email_template
from api.v1.routes.contact import contact
from api.v1.routes.permissions.permisions import perm_role
from api.v1.routes.permissions.roles import role_perm
from api.v1.routes.analytics import analytics
from api.v1.routes.job_application import job_application
from api.v1.routes.privacy import privacies
from api.v1.routes.settings import settings
from api.v1.routes.terms_and_conditions import terms_and_conditions
from api.v1.routes.stripe import subscription_

api_version_one = APIRouter(prefix="/api/v1")

api_version_one.include_router(api_status)
api_version_one.include_router(auth)
api_version_one.include_router(faq_inquiries)
api_version_one.include_router(google_auth)
api_version_one.include_router(fb_auth)
api_version_one.include_router(pwd_reset)
api_version_one.include_router(user_router)
api_version_one.include_router(profile)
api_version_one.include_router(organisation)
api_version_one.include_router(non_organisation_product)
api_version_one.include_router(product)
api_version_one.include_router(payment)
api_version_one.include_router(bill_plan)
api_version_one.include_router(notification)
api_version_one.include_router(notification_setting)
api_version_one.include_router(email_template)
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
api_version_one.include_router(news_sub)
api_version_one.include_router(testimonial)
api_version_one.include_router(test_rout)
api_version_one.include_router(email_sender)
api_version_one.include_router(regions)
api_version_one.include_router(test_router)
api_version_one.include_router(squeeze)
api_version_one.include_router(contact)
api_version_one.include_router(dashboard)
api_version_one.include_router(perm_role)
api_version_one.include_router(role_perm)
api_version_one.include_router(analytics)
api_version_one.include_router(job_application)
api_version_one.include_router(privacies)
api_version_one.include_router(settings)
api_version_one.include_router(team)
api_version_one.include_router(terms_and_conditions)
api_version_one.include_router(product_comment)
api_version_one.include_router(subscription_)
