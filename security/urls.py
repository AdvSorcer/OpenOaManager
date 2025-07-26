from django.urls import path
from . import views

app_name = 'security'

urlpatterns = [
    # 防火牆管理
    path('firewall/', views.firewall_list, name='firewall_list'),
    path('firewall/add/', views.firewall_add, name='firewall_add'),
    path('firewall/<int:pk>/', views.firewall_detail, name='firewall_detail'),
    path('firewall/<int:pk>/edit/', views.firewall_edit, name='firewall_edit'),
    path('firewall/<int:pk>/delete/', views.firewall_delete, name='firewall_delete'),

    # SSL 憑證管理
    path('ssl/', views.ssl_list, name='ssl_list'),
    path('ssl/add/', views.ssl_add, name='ssl_add'),
    path('ssl/<int:pk>/', views.ssl_detail, name='ssl_detail'),
    path('ssl/<int:pk>/edit/', views.ssl_edit, name='ssl_edit'),
    path('ssl/<int:pk>/delete/', views.ssl_delete, name='ssl_delete'),

    # VPN 管理
    path('vpn/', views.vpn_list, name='vpn_list'),
    path('vpn/add/', views.vpn_add, name='vpn_add'),
    path('vpn/<int:pk>/', views.vpn_detail, name='vpn_detail'),
    path('vpn/<int:pk>/delete/', views.vpn_delete, name='vpn_delete'),
] 