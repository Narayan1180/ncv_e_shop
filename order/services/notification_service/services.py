from ...models import Notification
from .providers import (
    EmailProvider,
    SMSProvider,
    PushProvider,
)


class NotificationService:

    providers = {
        Notification.Channel.EMAIL: EmailProvider,
        Notification.Channel.SMS: SMSProvider,
        Notification.Channel.PUSH: PushProvider,
    }

    @classmethod
    def send(cls, notification):

        provider_class = cls.providers.get(
            notification.channel
        )

        if not provider_class:
            raise ValueError(
                f"Unsupported channel: "
                f"{notification.channel}"
            )

        provider = provider_class()

        return provider.send(notification)

