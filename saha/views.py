# saha/views.py (Yeni View Eklendi)

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import admin

@login_required
def saha_dashboard(request):
    """
    SAHA & İŞ YÖNETİMİ modülünün ana paneli/dashboard'u için yer tutucu.
    """
    context = {
        **admin.site.each_context(request),
        'baslik': "Saha ve İş Yönetimi Paneli",
        'message': "Bu panoda, tahliye takibi özeti, iş takvimi (Gantt) ve günlük raporlar özetlenecektir."
    }
    # Geçici olarak Admin'in ana sayfa template'ini kullanalım
    return render(request, 'admin/index.html', context)