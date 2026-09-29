import razorpay
from django.conf import settings


class RazorpayGateway:

    def __init__(self):
        self.client = razorpay.Client(
            auth=(
                settings.RAZORPAY_KEY_ID,
                settings.RAZORPAY_SECRET,
            )
        )

    def create_payment_order(self, order):
        razorpay_order = self.client.order.create({
            "amount": int(order.total_amount * 100),  # INR → paise
            "currency": "INR",
            "receipt": f"order_{order.id}",
        })

        return razorpay_order

    def verify_payment_signature(self, data):
        return self.client.utility.verify_payment_signature(data)