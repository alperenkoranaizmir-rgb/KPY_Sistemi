from django.urls import path
from . import views

# Uygulama ad alanı tanımı (NameSpacing)
app_name = 'finance'

urlpatterns = [
    # Raporlar
    # Düzeltme: views.butce_raporu -> views.butce_vs_fiili_raporu
    path('butce-vs-fiili-raporu/', views.butce_vs_fiili_raporu, name='butce_vs_fiili_raporu'),
    
    # Diğer URL'ler buraya eklenecektir.
]