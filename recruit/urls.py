"""
URL configuration for recruit project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from recruit import views as recruit_views


urlpatterns = [
    path("admin/", admin.site.urls),
    path("healthcheck", recruit_views.health_check, name="health_check"),
    path("home", recruit_views.home_page, name='home'),
    path('start-call/', recruit_views.start_call, name='start_call'),
    path('send-invite/', recruit_views.send_invite, name='send_invite'),
    path('interview/<str:phone_number>/', recruit_views.interview, name='interview'),
    path('start-recording/', recruit_views.start_recording, name='start_recording'),
    path('stop-recording/', recruit_views.stop_recording, name='stop_recording'),
    path('video-webhook/', recruit_views.video_webhook, name='video_webhook'),
    path('recording-webhook/', recruit_views.recording_webhook, name='recording_webhook'),
]