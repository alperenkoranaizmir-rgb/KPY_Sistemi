from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import admin # Admin context için

@login_required
def toplu_bildirim(request):
    context = {
        **admin.site.each_context(request),
        'baslik': "Toplu SMS/E-Posta Gönderimi",
        'message': "Bu iletişim aracı sayfası henüz tamamlanmadı."
    }
    # Varsayılan bir template kullanıldı
    return render(request, 'admin/index.html', context)