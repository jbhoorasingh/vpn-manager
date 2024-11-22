from django.urls import path
from . import views

urlpatterns = [
    path('', views.TunnelRequestListView.as_view(), name='tunnel-list'),
    path('new/', views.TunnelRequestCreateView.as_view(), name='tunnel-create'),
    path('<int:pk>/', views.TunnelRequestDetailView.as_view(), name='tunnel-detail'),
    path('<int:pk>/approve/', views.TunnelApprovalView.as_view(), name='tunnel-approve'),
    path('<int:pk>/validate/', views.TunnelValidationView.as_view(), name='tunnel-validate'),
]