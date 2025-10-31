from django.urls import path
from django.views.generic import TemplateView

app_name = 'projects'

urlpatterns = [
    # Proje Listesi (Sidebar linki: projects:proje_listesi)
    path('listesi/', TemplateView.as_view(template_name='projects/proje_listesi.html'), name='proje_listesi'),
    
    # Dashboard linki: Malik Direnç Analizi (Sidebar linki: projects:direnc_analizi)
    path('direnc-analizi/', TemplateView.as_view(template_name='projects/direnc_analizi.html'), name='direnc_analizi'),

    # !!! HATA DÜZELTMESİ İÇİN EKLENEN RAPOR LİNKLERİ (templates/admin/index.html'den)
    path('direnc-analizi-raporu/', TemplateView.as_view(template_name='projects/direnc_analizi_raporu.html'), name='direnc_analizi_raporu'),
    path('ilerleme-hunisi-raporu/', TemplateView.as_view(template_name='projects/ilerleme_hunisi.html'), name='ilerleme_hunisi_raporu'), 

    # Diğer Proje Görünümleri buraya eklenecektir.
]