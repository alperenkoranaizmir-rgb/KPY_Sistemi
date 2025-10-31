# finance/urls.py

from django.urls import path
from . import views 
from django.contrib.auth.decorators import login_required

app_name = 'finance'

urlpatterns = [
    # JAZZMIN menüsündeki 'finance:butce_vs_fiili_raporu' named URL'si için
    path(
        'raporlar/butce-vs-fiili/', 
        login_required(views.butce_vs_fiili_raporu), 
        name='butce_vs_fiili_raporu'
    ),
    # Diğer finance view'ları buraya eklenecek
]