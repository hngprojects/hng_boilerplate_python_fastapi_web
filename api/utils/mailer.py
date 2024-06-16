import resend
from decouple import config

resend.api_key = config('RESEND_API_KEY')

class Mailer(resend.Emails):
    pass