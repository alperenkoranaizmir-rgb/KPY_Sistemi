# projects/urls.py dosyanızın içeriğini bu şekilde güncelleyin
from django.urls import path
from . import views 
from django.contrib.auth.decorators import login_required

app_name = 'projects'

urlpatterns = [
    # Malik Direnç Analizi Raporu (Mevcut)
    path(
        'raporlar/direnc-analizi/', 
        login_required(views.direnc_analizi_raporu),
        name='direnc_analizi_raporu'
    ),
    # YENİ EKLENEN: Proje İlerleme Hunisi Raporu
    path(
        'raporlar/ilerleme-hunisi/', 
        login_required(views.ilerleme_hunisi_raporu), 
        name='ilerleme_hunisi_raporu'
    ),
    # Diğer project view'ları buraya eklenecek
]