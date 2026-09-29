from django.conf import settings
from django.core.mail import send_mail
from twilio.rest import Client


class EmailProvider:

    def send(self, notification):

        send_mail(
            subject=notification.subject,
            message=notification.message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[notification.recipient],
        )


class SMSProvider:

    def __init__(self):

        self.client = Client(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN,
        )

    def send(self, notification):

        return self.client.messages.create(
            body=notification.message,
            from_=settings.TWILIO_FROM_NUMBER,
            to=notification.recipient,
        )


class PushProvider:

    def send(self, notification):

        # Firebase/FCM implementation later
        print(
            f"Push notification → "
            f"{notification.recipient}: "
            f"{notification.message}"
        )