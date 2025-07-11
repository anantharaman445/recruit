import json
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from recruit.platform.send_sms import SendSmsFromTwilio
from recruit.platform.token import GenerateTwtilioAccessToken
from recruit.platform.video_call import VideoCallRecording
import uuid

# Static data storage (in-memory for now)
interviews_data = {}
recording_sessions = {}

NGROK_URL= "https://3d31ca1c7df7.ngrok-free.app"

def health_check(request):
    data = {'message': 'OK'}
    return JsonResponse(status=200, data=data)

def home_page(request):
    return render(request, 'home.html')

@csrf_exempt
def send_invite(request):
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        
        if not phone_number:
            messages.error(request, 'Phone number is required')
            return redirect('home')
        # Generate interview link
        interview_link = request.build_absolute_uri(f'/interview/{phone_number}/')
        # interview_link = f'{NGROK_URL}/interview/{phone_number}'
        
        # Send SMS
        try:
            body=f'You have been invited for a video interview. Please click the link to start: {interview_link}',
            sms_action = SendSmsFromTwilio(
                message_body=body,
                to_phone_number=phone_number
                )
            sms_action.execute()
            # Store interview data
            interviews_data[phone_number] = {
                'status': 'invited',
                'recordings': {},
                'interview_id': str(uuid.uuid4())
            }
            
            messages.success(request, f'Interview invitation sent to {phone_number}')
            return redirect('home')
            
        except Exception as e:
            messages.error(request, f'Failed to send SMS: {str(e)}')
            return redirect('home')
    
    return redirect('home')

@csrf_exempt
def interview(request, phone_number):
    # print("interviews_data", interviews_data)
    interviews_data = {'+917871903816': {'status': 'invited', 'recordings': {}, 'interview_id': 'd7fac306-951c-4427-a115-40b6904aab40'}}
    if phone_number not in interviews_data:
        return HttpResponse('Invalid interview link', status=404)
    
    interview_data = interviews_data[phone_number]
    questions = [
        {'id': 1, 'text': 'Tell me about yourself'},
        {'id': 2, 'text': 'Why do you want to join our organization?'}
    ]
    
    context = {
        'phone_number': phone_number,
        'interview_id': interview_data['interview_id'],
        'questions': questions
    }
    
    return render(request, 'interview.html', context)

@csrf_exempt
def start_call(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        phone_number = data.get('phone_number')
        question_id = data.get('question_id')
        
        token, room_name = GenerateTwtilioAccessToken().generate_video_call_token(phone_number, question_id)
        
        return JsonResponse({
            'access_token': token,
            'room_name': room_name
        })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@csrf_exempt
def video_status(request):
    # Webhook to handle video call status updates
    if request.method == 'POST':
        # Handle Twilio webhook for video status
        return HttpResponse('OK')
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def start_recording(request):
    data = json.loads(request.body)
    phone_number = data.get('phone_number')
    question_id = data.get('question_id')
    room_sid = data.get('room_sid')
    interviews_data = {'+917871903816': {'status': 'invited', 'recordings': {}, 'interview_id': 'd7fac306-951c-4427-a115-40b6904aab40'}}
    if phone_number not in interviews_data:
        return JsonResponse({'error': 'Interview not found'}, status=404)
    url = request.build_absolute_uri('/video-webhook/')
    success, result = VideoCallRecording().start_video_call_recording(room_sid, phone_number, question_id, url)
    if not success:
        return JsonResponse({'error': 'Failed to start recording'}, status=500)
    composition_sid = result

    recording_sessions[composition_sid] = {
            'phone_number': phone_number,
            'question_id': question_id,
            'room_sid': room_sid,
            'status': 'recording'
        }
    
    return JsonResponse({
            'composition_sid': composition_sid,
            'status': 'recording_started'
        })


@csrf_exempt
def stop_recording(request):
    data = json.loads(request.body)
    composition_sid = data.get('composition_sid')
    
    if not composition_sid or composition_sid not in recording_sessions:
        return JsonResponse({'error': 'Recording session not found'}, status=404)
    
    success, result = VideoCallRecording().stop_video_call_recording(composition_sid)
    if not success:
        return JsonResponse({'error': 'Failed to stop recording'}, status=500)
    
    composition_sid = result

    recording_sessions[composition_sid]['status'] = 'stopped'
    return JsonResponse({
        'composition_sid': composition_sid,
        'status': 'recording_stopped'
    })

@csrf_exempt
def video_webhook(request):
    """Handle Twilio Video webhooks"""
    if request.method == 'POST':
        try:
            # Parse webhook data
            room_sid = request.POST.get('RoomSid')
            room_status = request.POST.get('StatusCallbackEvent')
            
            print(f"Video webhook: Room {room_sid} - Status: {room_status}")
            
            return HttpResponse('OK', status=200)
            
        except Exception as e:
            print(f"Error processing video webhook: {str(e)}")
            return HttpResponse('Error', status=500)
    if request.method == 'GET':
        print("Get record composition", request.GET)
        return HttpResponse('OK', status=200)
        
    
    return HttpResponse('Method not allowed', status=405)

@csrf_exempt
def recording_webhook(request):
    """Handle Twilio Recording webhooks"""
    if request.method == 'POST':
        try:
            # Parse webhook data
            recording_sid = request.POST.get('RecordingSid')
            recording_status = request.POST.get('StatusCallbackEvent')
            media_url = request.POST.get('MediaUrl')
            
            print(f"Recording webhook: {recording_sid} - Status: {recording_status}")
            
            if recording_sid in recording_sessions:
                session_info = recording_sessions[recording_sid]
                phone_number = session_info['phone_number']
                question_id = session_info['question_id']
                
                # Update interview data with recording info
                if recording_status == 'recording-completed' and media_url:
                    interviews_data[phone_number]['recordings'][question_id] = {
                        'recording_sid': recording_sid,
                        'media_url': media_url,
                        'status': 'completed'
                    }
                    
                    # Download and save recording locally (optional)
                    # download_recording(recording_sid, media_url, phone_number, question_id)
                
                # Update session status
                recording_sessions[recording_sid]['status'] = recording_status
            
            return HttpResponse('OK', status=200)
            
        except Exception as e:
            print(f"Error processing recording webhook: {str(e)}")
            return HttpResponse('Error', status=500)
    
    return HttpResponse('Method not allowed', status=405)
