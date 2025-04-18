# from django.contrib import admin
# from django.urls import path, include

# urlpatterns = [
# path('admin/', admin.site.urls),
# path('api/', include('app.urls')),
# ]

from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

def home(request):
    return HttpResponse("Welcome to the Seismic Salt Segmentation App!")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('app.urls')),
    path('', home),  # <--- This will handle requests to /
]
