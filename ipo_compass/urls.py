from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('ipo_app.urls')),  # 👈 make sure app name matches your folder
]
