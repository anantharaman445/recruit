import os
from twilio.rest import Client

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
TWILIO_API_KEY = os.getenv("TWILIO_API_KEY")
TWILIO_API_SECRET = os.getenv("TWILIO_API_SECRET")



class VideoCallRecording:

    @staticmethod
    def start_video_call_recording(room_sid, phone_number, question_id, call_back_url):
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

        try:
            if not room_sid:
                room = client.video.rooms.create(
                    unique_name=f"interview_{phone_number}_{question_id}",
                    type='group'
                )
                room_sid = room.sid
            
            # Start recording
            recording = client.video.recordings.create(
                room_sid=room_sid,
                status_callback=call_back_url,
                status_callback_method='POST'
            )
        except Exception as e:
            print(f"Failed to start recording: {str(e)}")
            return False, None
        return True, recording.sid

    @staticmethod
    def stop_video_call_recording(recording_sid):
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        try:
            recording = client.video.recordings(recording_sid).update(status='stopped')
             return True, recording_sid
        except Exception as e:
            print(f"Failed to stop recording: {str(e)}")
            return False, None