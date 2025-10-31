from django.urls import path
from django.views.generic import TemplateView
from .views import DashboardView

app_name = 'users'

urlpatterns = [
    # Kullanıcının kendi dashboard sayfası (Ana Sayfa)
    path('', DashboardView.as_view(), name='dashboard'),
    
    # Görev Listesi Sayfası (Sidebar ve Dashboard linki: users:gorev_listesi)
    # Bir sonraki adımda bu View'ı (GorevListView) oluşturacağız, şimdilik TemplateView kullanıyoruz.
    path('gorevler/', TemplateView.as_view(template_name='users/gorev_listesi.html'), name='gorev_listesi'), 
]