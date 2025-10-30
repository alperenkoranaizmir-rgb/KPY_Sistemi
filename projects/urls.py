from django.urls import path
from . import views

# KRİTİK DÜZELTME: Bu URL grubuna "projects" adında bir isim alanı (namespace) veriyoruz.
app_name = 'projects'

urlpatterns = [
    # Rapor adı artık 'projects:direnc_analizi_raporu' olarak kullanılabilir.
    path('rapor/direnc/', views.direnc_analizi_raporu, name='direnc_analizi_raporu'),
]