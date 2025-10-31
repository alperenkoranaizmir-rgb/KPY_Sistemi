from django.urls import path
from django.views.generic import TemplateView

app_name = 'saha'

urlpatterns = [
    # Günlük Saha Raporları (Sidebar linki: saha:saha_rapor_listesi)
    path('gunluk-raporlar/', TemplateView.as_view(template_name='saha/saha_rapor_listesi.html'), name='saha_rapor_listesi'),
    
    # Kalite Kontrol (QC) Formları (Sidebar linki: saha:qc_form_listesi)
    path('qc-formlari/', TemplateView.as_view(template_name='saha/qc_form_listesi.html'), name='qc_form_listesi'),
    
    # Tahliye Takibi (Sidebar linki: saha:tahliye_takibi)
    path('tahliye/', TemplateView.as_view(template_name='saha/tahliye_takibi.html'), name='tahliye_takibi'),

    # Diğer Saha Görünümleri buraya eklenecektir.
]