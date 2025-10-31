# users/urls.py

from django.urls import path
from . import views 
from django.contrib.auth.decorators import login_required

app_name = 'users'

urlpatterns = [
    # JAZZMIN menüsündeki 'users:toplu_bildirim' named URL'si için
    path(
        'bildirim/toplu-gonderim/', 
        login_required(views.toplu_bildirim), 
        name='toplu_bildirim'
    ),
]