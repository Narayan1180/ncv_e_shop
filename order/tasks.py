from celery import shared_task
from django.core.mail import send_mail,EmailMessage
from django.conf import settings

from django.template.loader import render_to_string
from weasyprint import HTML
from .models import Order

@shared_task
def send_order_email(order_id,email):
    print("hi")
    #print(f"Sending email for order {order_id}")
    send_mail(
        subject='Hello from Celery',
        message=f'hi your order is confirmed! for {order_id} will be delivered within 2-3 working days.Thank you for shopping with us ',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email],
    )

    order = Order.objects.get(id=order_id)
    html_string = render_to_string("order/order_invoice_pdf.html", {"order": order})
    pdf_bytes = HTML(string=html_string).write_pdf()

    email = EmailMessage(
        subject=f"Invoice for Order {order_id}",
        body="Please find your invoice attached.",
        to=[order.user.email],
    )
    email.attach(f"invoice_{order.id}.pdf", pdf_bytes, "application/pdf")
    email.send()



from celery import shared_task
from django.utils import timezone

from .models import Notification
from .services import NotificationService


@shared_task( bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_jitter=True, max_retries=3, )
def send_notification(self, notification_id):

    notification = Notification.objects.get( id=notification_id )

    # Idempotency protection
    if notification.status == Notification.Status.SENT:
        return

    notification.attempts += 1
    notification.save(update_fields=["attempts"])

    try:

        NotificationService.send(notification)

        notification.status = (Notification.Status.SENT)

        notification.sent_at = timezone.now()

        notification.save( update_fields=[ "status", "sent_at", ] )

    except Exception:

        notification.status = ( Notification.Status.FAILED )

        notification.failed_at = timezone.now()

        notification.save( update_fields=[ "status", "failed_at", ] )

        raise


def create_mail_notification(user,order):
    notification = Notification.objects.create(
    user=user,
    channel=Notification.Channel.EMAIL,
    recipient=user.email,
    subject="Order Confirmation",
    message=( f"Hi, your order {order.id} is confirmed. " "It will be delivered within 2-3 working days." ),
    idempotency_key=( f"order-{order.id}-confirmation-email" ),
    )

    return notification.id



def create_msg_notifications(user,order):
    notification = Notification.objects.create(
    user=user,
    channel=Notification.Channel.SMS,
    recipient="+916283952017",
    message="sms_order_confirmation",
    idempotency_key=( f"order-{order.id}-confirmation-sms" ),
    )

    return notification.id



    


