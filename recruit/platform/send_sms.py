from twilio.rest import Client
import os

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")


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
