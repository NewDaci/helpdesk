from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.http import JsonResponse

urlpatterns = [
    # welcoming page
    path('', lambda request: JsonResponse({"message": "Welcome to Helpdesk API. Visit /api/docs/ for API documentation."})),
    path('admin/', admin.site.urls),

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema')),

    path('auth/login/', TokenObtainPairView.as_view()),
    path('auth/refresh/', TokenRefreshView.as_view()),

    path('accounts/', include('accounts.urls')),
    path('tickets/', include('tickets.urls')),
]
