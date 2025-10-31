from django.urls import path
from django.views.generic import TemplateView # Placeholder view'ler için

app_name = 'envanter'

urlpatterns = [
    # Demirbaş Listesi (Sidebar linki: envanter:envanter_listesi)
    path('demirbaslar/', TemplateView.as_view(template_name='envanter/listeler/envanter_listesi.html'), name='envanter_listesi'),
    
    # Stok Durumu (Sidebar linki: envanter:stok_durumu)
    path('stok/', TemplateView.as_view(template_name='envanter/listeler/stok_durumu.html'), name='stok_durumu'),

    # Diğer Envanter Görünümleri buraya eklenecektir.
]