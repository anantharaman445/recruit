import json
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from recruit.platform.send_sms import SendSmsFromTwilio
from recruit.platform.token import GenerateTwtilioAccessToken
import uuid

# Static data storage (in-memory for now)
interviews_data = {}


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
        # interview_link = f'https://66e9a6df7c52.ngrok-free.app/interview/{phone_number}'
        
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
    # interviews_data = {'+917871903816': {'status': 'invited', 'recordings': {}, 'interview_id': '3037138f-7b4a-44b9-a4ff-4d8fcb2609d6'}}
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
def save_recording(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        phone_number = data.get('phone_number')
        question_id = data.get('question_id')
        recording_url = data.get('recording_url')
        
        if phone_number in interviews_data:
            interviews_data[phone_number]['recordings'][question_id] = recording_url
            interviews_data[phone_number]['status'] = 'completed'
            
            return JsonResponse({'status': 'success'})
        
        return JsonResponse({'error': 'Interview not found'}, status=404)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)