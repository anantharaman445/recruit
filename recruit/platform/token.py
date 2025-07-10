from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VideoGrant

import os




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
