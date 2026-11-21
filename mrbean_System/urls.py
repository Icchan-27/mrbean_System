from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from accounts.views import login_view
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('management/', include('management.urls')),
    path('', lambda request: redirect('login')),

    path('admin/', admin.site.urls),

    path('pos/', include('PoS.urls')),
    path('inventory/', include('Inventory.urls')),

    path('', include('accounts.urls')),

    path('login/', login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)