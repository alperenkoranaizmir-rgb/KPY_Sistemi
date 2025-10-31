from django.urls import path
from django.views.generic import TemplateView

app_name = 'finance'

urlpatterns = [
    # Bütçe Raporu (Sidebar linki: finance:butce_raporu)
    path('butce-raporu/', TemplateView.as_view(template_name='finance/butce_raporu.html'), name='butce_raporu'),
    
    # Fatura Listesi (Sidebar linki: finance:fatura_listesi)
    path('faturalar/', TemplateView.as_view(template_name='finance/fatura_listesi.html'), name='fatura_listesi'),
    
    # Harcama Talep Listesi (Sidebar linki: finance:harcama_talep_listesi)
    path('harcama-talepleri/', TemplateView.as_view(template_name='finance/harcama_talep_listesi.html'), name='harcama_talep_listesi'),

    # !!! HATA DÜZELTMESİ İÇİN EKLENEN RAPOR LİNKİ (templates/admin/index.html'den)
    path('butce-vs-fiili-raporu/', TemplateView.as_view(template_name='finance/butce_vs_fiili_raporu.html'), name='butce_vs_fiili_raporu'),

    # Diğer Finans Görünümleri buraya eklenecektir.
]