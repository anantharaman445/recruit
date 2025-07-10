# requirements.txt
Django==4.2.7
twilio==8.11.0
python-decouple==3.8

# settings.py
import os
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='your-secret-key-here')
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'interview_app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'interview_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Twilio Configuration
TWILIO_ACCOUNT_SID = config('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = config('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = config('TWILIO_PHONE_NUMBER')

# Static files
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# urls.py (main project)
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('interview_app.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# interview_app/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('send-invite/', views.send_invite, name='send_invite'),
    path('interview/<str:phone_number>/', views.interview, name='interview'),
    path('start-call/', views.start_call, name='start_call'),
    path('video-status/', views.video_status, name='video_status'),
    path('save-recording/', views.save_recording, name='save_recording'),
]

# interview_app/views.py
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from twilio.rest import Client
from twilio.twiml import TwiML
from django.conf import settings
import json
import uuid
import os

# Static data storage (in-memory for now)
interviews_data = {}

def home(request):
    return render(request, 'home.html')

def send_invite(request):
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        
        if not phone_number:
            messages.error(request, 'Phone number is required')
            return redirect('home')
        
        # Initialize Twilio client
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        
        # Generate interview link
        interview_link = request.build_absolute_uri(f'/interview/{phone_number}/')
        
        # Send SMS
        try:
            message = client.messages.create(
                body=f'You have been invited for a video interview. Please click the link to start: {interview_link}',
                from_=settings.TWILIO_PHONE_NUMBER,
                to=phone_number
            )
            
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

@csrf_exempt
def start_call(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        phone_number = data.get('phone_number')
        question_id = data.get('question_id')
        
        # Generate access token for Twilio Video
        from twilio.jwt.access_token import AccessToken
        from twilio.jwt.access_token.grants import VideoGrant
        
        # Create access token
        token = AccessToken(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_API_KEY_SID,  # You'll need to create this in Twilio Console
            settings.TWILIO_API_KEY_SECRET,  # You'll need to create this in Twilio Console
            identity=f"candidate_{phone_number}"
        )
        
        # Create a video grant for the room
        room_name = f"interview_{phone_number}_{question_id}"
        video_grant = VideoGrant(room=room_name)
        token.add_grant(video_grant)
        
        return JsonResponse({
            'access_token': token.to_jwt(),
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

# templates/base.html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Interview Screening App{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .video-container {
            position: relative;
            width: 100%;
            height: 400px;
            background-color: #000;
            border-radius: 8px;
            overflow: hidden;
        }
        
        .video-controls {
            position: absolute;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            display: flex;
            gap: 10px;
        }
        
        .question-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        
        .recording-indicator {
            position: absolute;
            top: 20px;
            right: 20px;
            background: #dc3545;
            color: white;
            padding: 5px 10px;
            border-radius: 20px;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="{% url 'home' %}">Interview Screening</a>
        </div>
    </nav>

    <div class="container mt-4">
        {% if messages %}
            {% for message in messages %}
                <div class="alert alert-{{ message.tags }} alert-dismissible fade show" role="alert">
                    {{ message }}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            {% endfor %}
        {% endif %}

        {% block content %}{% endblock %}
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://sdk.twilio.com/js/video/releases/2.26.0/twilio-video.min.js"></script>
</body>
</html>

# templates/home.html
{% extends 'base.html' %}

{% block title %}Send Interview Invitation{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h3>Send Interview Invitation</h3>
            </div>
            <div class="card-body">
                <form method="post" action="{% url 'send_invite' %}">
                    {% csrf_token %}
                    <div class="mb-3">
                        <label for="phone_number" class="form-label">Candidate Phone Number</label>
                        <input type="tel" class="form-control" id="phone_number" name="phone_number" 
                               placeholder="+1234567890" required>
                        <div class="form-text">Include country code (e.g., +1 for US)</div>
                    </div>
                    <button type="submit" class="btn btn-primary">Send Interview Link</button>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}

# templates/interview.html
{% extends 'base.html' %}

{% block title %}Video Interview{% endblock %}

{% block content %}
<div class="row">
    <div class="col-md-8">
        <div class="video-container" id="video-container">
            <div id="local-video"></div>
            <div class="recording-indicator" id="recording-indicator" style="display: none;">
                ● Recording
            </div>
            <div class="video-controls">
                <button class="btn btn-danger" id="start-recording" onclick="startRecording()">
                    Start Recording
                </button>
                <button class="btn btn-secondary" id="stop-recording" onclick="stopRecording()" style="display: none;">
                    Stop Recording
                </button>
                <button class="btn btn-success" id="next-question" onclick="nextQuestion()" style="display: none;">
                    Next Question
                </button>
            </div>
        </div>
    </div>
    
    <div class="col-md-4">
        <div class="question-card">
            <h5>Interview Questions</h5>
            <div id="questions-list">
                {% for question in questions %}
                <div class="question-item" data-question-id="{{ question.id }}">
                    <strong>Question {{ question.id }}:</strong> {{ question.text }}
                    <span class="badge bg-secondary ms-2" id="status-{{ question.id }}">Pending</span>
                </div>
                <hr>
                {% endfor %}
            </div>
        </div>
        
        <div class="card mt-3">
            <div class="card-body">
                <h6>Instructions:</h6>
                <ul>
                    <li>Click "Start Recording" to begin your answer</li>
                    <li>Speak clearly and look at the camera</li>
                    <li>Click "Stop Recording" when finished</li>
                    <li>Click "Next Question" to proceed</li>
                </ul>
            </div>
        </div>
    </div>
</div>

<script>
let currentRoom = null;
let currentQuestionIndex = 0;
let isRecording = false;
let localVideoTrack = null;
let questions = {{ questions|safe }};
let phoneNumber = "{{ phone_number }}";

// Initialize video call
async function initializeVideo() {
    try {
        // Get access token from server
        const response = await fetch('/start-call/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                phone_number: phoneNumber,
                question_id: questions[currentQuestionIndex].id
            })
        });
        
        const data = await response.json();
        
        // Connect to Twilio Video room
        const room = await Twilio.Video.connect(data.access_token, {
            name: data.room_name,
            audio: true,
            video: true
        });
        
        currentRoom = room;
        
        // Display local video
        room.localParticipant.videoTracks.forEach(publication => {
            const videoElement = publication.track.attach();
            videoElement.style.width = '100%';
            videoElement.style.height = '100%';
            videoElement.style.objectFit = 'cover';
            document.getElementById('local-video').appendChild(videoElement);
        });
        
        // Show current question
        showCurrentQuestion();
        
    } catch (error) {
        console.error('Error initializing video:', error);
        alert('Failed to initialize video. Please check your camera and microphone permissions.');
    }
}

function showCurrentQuestion() {
    // Highlight current question
    document.querySelectorAll('.question-item').forEach(item => {
        item.style.backgroundColor = '';
    });
    
    const currentQuestionElement = document.querySelector(`[data-question-id="${questions[currentQuestionIndex].id}"]`);
    if (currentQuestionElement) {
        currentQuestionElement.style.backgroundColor = '#e3f2fd';
    }
}

function startRecording() {
    isRecording = true;
    document.getElementById('recording-indicator').style.display = 'block';
    document.getElementById('start-recording').style.display = 'none';
    document.getElementById('stop-recording').style.display = 'inline-block';
    
    // Update question status
    document.getElementById(`status-${questions[currentQuestionIndex].id}`).textContent = 'Recording';
    document.getElementById(`status-${questions[currentQuestionIndex].id}`).className = 'badge bg-danger ms-2';
}

function stopRecording() {
    isRecording = false;
    document.getElementById('recording-indicator').style.display = 'none';
    document.getElementById('stop-recording').style.display = 'none';
    document.getElementById('next-question').style.display = 'inline-block';
    
    // Update question status
    document.getElementById(`status-${questions[currentQuestionIndex].id}`).textContent = 'Completed';
    document.getElementById(`status-${questions[currentQuestionIndex].id}`).className = 'badge bg-success ms-2';
    
    // Save recording (simulated)
    saveRecording();
}

async function saveRecording() {
    try {
        const response = await fetch('/save-recording/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                phone_number: phoneNumber,
                question_id: questions[currentQuestionIndex].id,
                recording_url: `recording_${phoneNumber}_${questions[currentQuestionIndex].id}.mp4`
            })
        });
        
        const data = await response.json();
        console.log('Recording saved:', data);
        
    } catch (error) {
        console.error('Error saving recording:', error);
    }
}

function nextQuestion() {
    currentQuestionIndex++;
    
    if (currentQuestionIndex < questions.length) {
        // Show next question
        showCurrentQuestion();
        document.getElementById('next-question').style.display = 'none';
        document.getElementById('start-recording').style.display = 'inline-block';
    } else {
        // Interview completed
        alert('Interview completed! Thank you for your time.');
        if (currentRoom) {
            currentRoom.disconnect();
        }
        window.location.href = '/';
    }
}

// Initialize video when page loads
window.addEventListener('load', initializeVideo);
</script>
{% endblock %}