from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'tunnels', views.TunnelRequestViewSet, basename='api-tunnel')

urlpatterns = [
    path('', include(router.urls)),
    path('tunnels/<int:pk>/validate/', views.TunnelRequestViewSet.as_view({'post': 'validate'}), name='api-tunnel-validate'),
]