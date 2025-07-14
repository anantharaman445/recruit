from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VideoGrant
from twilio.rest import Client

import os

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
TWILIO_API_KEY = os.getenv("TWILIO_API_KEY")
TWILIO_API_SECRET = os.getenv("TWILIO_API_SECRET")


class GenerateTwtilioAccessToken:
    @staticmethod
    def generate_video_call_token(phone_number, room_id):
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        token = AccessToken(
            TWILIO_ACCOUNT_SID,
            TWILIO_API_KEY,  # You'll need to create this in Twilio Console
            TWILIO_API_SECRET,  # You'll need to create this in Twilio Console
            identity=f"candidate_{phone_number}"
        )

        room_name = f"interview_{phone_number}_{room_id}"
        # room = client.video.rooms.create(
        #             unique_name=f"interview_{phone_number}_{question_id}", type="group",
        #             recordParticipantsOnConnect=True,
        #         )
        video_grant = VideoGrant(room=room_name)
        token.add_grant(video_grant)
        return token.to_jwt(), room_name
