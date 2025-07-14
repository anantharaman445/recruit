import os
from twilio.rest import Client

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
TWILIO_API_KEY = os.getenv("TWILIO_API_KEY")
TWILIO_API_SECRET = os.getenv("TWILIO_API_SECRET")



def get_room_participants(client, room_sid):
    """
    Get all participants currently in the room

    Args:
        room_sid (str): The SID of the room

    Returns:
        list: List of participant identities and their track info
    """
    try:
        # Get room details
        room = client.video.v1.rooms(room_sid).fetch()

        # Get participants
        participants = client.video.v1.rooms(room_sid).participants.list(
            status="connected"
        )

        participant_info = []
        for participant in participants:
            # Get published tracks for each participant
            published_tracks = (
                client.video.v1.rooms(room_sid)
                .participants(participant.sid)
                .published_tracks.list()
            )

            tracks = {"video_tracks": [], "audio_tracks": [], "data_tracks": []}

            for track in published_tracks:
                if track.kind == "video":
                    tracks["video_tracks"].append(track.sid)
                elif track.kind == "audio":
                    tracks["audio_tracks"].append(track.sid)
                elif track.kind == "data":
                    tracks["data_tracks"].append(track.sid)

            participant_info.append(
                {
                    "identity": participant.identity,
                    "sid": participant.sid,
                    "status": participant.status,
                    "tracks": tracks,
                    "has_video": len(tracks["video_tracks"]) > 0,
                    "has_audio": len(tracks["audio_tracks"]) > 0,
                }
            )

        return participant_info

    except Exception as e:
        print(f"Error getting room participants: {str(e)}")
        return []


class VideoCallRecording:

    @staticmethod
    def start_video_call_recording(room_sid, phone_number, question_id, call_back_url):
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

        try:
            print("room_sid", room_sid)
            if not room_sid:
                room = client.video.rooms.create(
                    unique_name=f"interview_{phone_number}_{question_id}", type="group",
                    recordParticipantsOnConnect=True,
                )
                room_sid = room.sid

            participants = get_room_participants(client, room_sid)

            participants_with_video = [p for p in participants if p["has_video"]]
            participants_with_audio = [p for p in participants if p["has_audio"]]

            participants_with_video = [
                p["identity"] for p in participants_with_video if p["has_video"]
            ]
            audio_sources = (
                participants_with_audio if participants_with_audio else ["*"]
            )

            if participants_with_video:
                video_layout = {
                    "grid": {
                        "video_sources": ['*']  # Specific participants instead of "*"
                    }
                }
            else:
                # Audio-only composition if no video
                video_layout = {}

            composition_params = {
                "room_sid": room_sid,
                "audio_sources": audio_sources,
                "format": "mp4",
                "status_callback_method": "POST",
            }

            if video_layout:
                composition_params["video_layout"] = video_layout

            if call_back_url:
                composition_params["status_callback"] = call_back_url

            composition = client.video.compositions.create(**composition_params)

            composition_sid = composition.sid
            print("composition_sid from start", composition_sid)
        except Exception as e:
            print(f"Failed to start recording: {str(e)}")
            return False, None
        return True, composition_sid

    @staticmethod
    def stop_video_call_recording(composition_sid):
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        try:
            composition = client.video.v1.compositions(composition_sid).fetch()
            print("composition from stop", composition)
            print("compositionsid", composition_sid)
            # composition.stop()
            return True, composition_sid
        except Exception as e:
            print(f"Failed to stop recording: {str(e)}")
            return False, None
