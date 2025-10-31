# saha/urls.py (Güncellenmiş)

from django.urls import path
from . import views 
from django.contrib.auth.decorators import login_required

app_name = 'saha'

urlpatterns = [
    # Saha Yönetimi ana paneli (İleride eklenecek, şimdilik admin index'e yönlendirilebilir)
    path(
        '', 
        login_required(views.saha_dashboard), 
        name='saha_dashboard'
    ),
    # İleride eklenecek diğer raporlar buraya gelecektir
    # path('raporlar/aktivite-raporu/', ..., name='aktivite_raporu'),
]