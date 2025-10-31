from django.urls import path
from . import views

# Uygulama ad alanı tanımı (NameSpacing)
app_name = 'projects'

urlpatterns = [
    # Raporlar
    # Düzeltme: views.direnc_analizi -> views.direnc_analizi_raporu
    path('direnc-analizi-raporu/', views.direnc_analizi_raporu, name='direnc_analizi_raporu'),
    
    # Düzeltme: views.ilerleme_hunisi -> views.ilerleme_hunisi_raporu
    path('ilerleme-hunisi-raporu/', views.ilerleme_hunisi_raporu, name='ilerleme_hunisi_raporu'),

    # Diğer URL'ler buraya eklenecektir.
]