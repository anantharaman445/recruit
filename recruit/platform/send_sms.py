from twilio.rest import Client
import os

# TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
# TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
# TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

TWILIO_ACCOUNT_SID="AC96d8fcdd6ccb844f9986e005771dadd4"
TWILIO_AUTH_TOKEN="1dc6411f8fb33fa25be5f46a11aa8981"
TWILIO_PHONE_NUMBER="+17242788234"
TWILIO_API_KEY="SK7fd6a271dbcabc4ba7227a68b3314b79"
TWILIO_API_SECRET="J02dzhl3k8kdAE8c9NX1ueXW9zvcerU1"

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


class SendSmsFromTwilio:
    def __init__(self, message_body, to_phone_number):
        self.message_body = message_body
        self.to_phone_number = to_phone_number

    def execute(self):
        success = True
        try:
            message = client.messages.create(
                body=self.message_body,
                from_=TWILIO_PHONE_NUMBER,
                to=self.to_phone_number,
            )
        except Exception as e:
            success = False
            message = str(e)
        return success, message
