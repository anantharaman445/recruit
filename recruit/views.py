import os
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from recruit.platform.send_sms import SendSmsFromTwilio
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