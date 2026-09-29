from django.conf import settings
from twilio.rest import Client

from twilio.rest import Client

def send_sms(phone, message):
    client = Client(
        settings.TWILIO_ACCOUNT_SID,
        settings.TWILIO_AUTH_TOKEN,
    )
    
    # Correct way to list approved Content API templates
   # templates = client.content.v1.contents.list(limit=20)
    #for t in templates:
        # Templates are stored as key-value structures
        #print(f"Template SID: {t.sid} | Name: {t.friendly_name}")
        
    # Sending a standard free-form text message
    response = client.messages.create(
        body=message,
        from_=settings.TWILIO_FROM_NUMBER,
        to=phone,
    )

    return response.sid

# Define the format string
message_body = "Your appointment is confirmed for sms_appointment_reminders"
# Construct the dynamic message body

# Pass it straight to your send_sms function
Template="Appointments Reminders"
#sms_order_confirmation="hey your order is confirmed"


if "__name__"=="__main__":
    
    send_sms("+916283952017","sms_order_confirmation")

#print(send_sms("+916283952017","Thank you for your order! Order #[Number] is confirmed. Track your package here: [Link]."))
