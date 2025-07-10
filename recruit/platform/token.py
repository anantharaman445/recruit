from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VideoGrant

import os

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
TWILIO_API_KEY="SK7fd6a271dbcabc4ba7227a68b3314b79"
TWILIO_API_SECRET="J02dzhl3k8kdAE8c9NX1ueXW9zvcerU1"


class GenerateTwtilioAccessToken:
    @staticmethod
    def generate_video_call_token(phone_number, room_id):
        token = AccessToken(
            TWILIO_ACCOUNT_SID,
            TWILIO_API_KEY,  # You'll need to create this in Twilio Console
            TWILIO_API_SECRET,  # You'll need to create this in Twilio Console
            identity=f"candidate_{phone_number}"
        )

        room_name = f"interview_{phone_number}_{room_id}"
        video_grant = VideoGrant(room=room_name)
        token.add_grant(video_grant)
        return token.to_jwt()
