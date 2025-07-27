from django.urls import path
from . import views

app_name = 'assets'

urlpatterns = [
    # 主頁 - 直接導向硬體資產列表
    path('', views.HardwareAssetListView.as_view(), name='dashboard'),
    
    # 硬體資產
    path('hardware/', views.HardwareAssetListView.as_view(), name='hardware_list'),
    path('hardware/<int:pk>/', views.HardwareAssetDetailView.as_view(), name='hardware_detail'),
    path('hardware/add/', views.HardwareAssetCreateView.as_view(), name='hardware_add'),
    path('hardware/<int:pk>/edit/', views.HardwareAssetUpdateView.as_view(), name='hardware_edit'),
    path('hardware/<int:pk>/delete/', views.HardwareAssetDeleteView.as_view(), name='hardware_delete'),
    
    # 軟體授權
    path('software/', views.SoftwareLicenseListView.as_view(), name='software_list'),
    path('software/<int:pk>/', views.SoftwareLicenseDetailView.as_view(), name='software_detail'),
    path('software/add/', views.SoftwareLicenseCreateView.as_view(), name='software_add'),
    path('software/<int:pk>/edit/', views.SoftwareLicenseUpdateView.as_view(), name='software_edit'),
    path('software/<int:pk>/delete/', views.SoftwareLicenseDeleteView.as_view(), name='software_delete'),
    
    # 供應商
    path('vendors/', views.VendorListView.as_view(), name='vendor_list'),
    path('vendors/<int:pk>/', views.VendorDetailView.as_view(), name='vendor_detail'),
    path('vendors/add/', views.VendorCreateView.as_view(), name='vendor_add'),
    path('vendors/<int:pk>/edit/', views.VendorUpdateView.as_view(), name='vendor_edit'),
    path('vendors/<int:pk>/delete/', views.VendorDeleteView.as_view(), name='vendor_delete'),
    
    # 採購申請
    path('purchase/', views.PurchaseRequestListView.as_view(), name='purchase_list'),
    path('purchase/<int:pk>/', views.PurchaseRequestDetailView.as_view(), name='purchase_detail'),
    path('purchase/add/', views.PurchaseRequestCreateView.as_view(), name='purchase_add'),
    path('purchase/<int:pk>/edit/', views.PurchaseRequestUpdateView.as_view(), name='purchase_edit'),
    path('purchase/<int:pk>/delete/', views.PurchaseRequestDeleteView.as_view(), name='purchase_delete'),
    path('purchase/<int:pk>/approve/', views.PurchaseRequestApprovalView.as_view(), name='purchase_approve'),
    
    # 維修記錄
    path('maintenance/', views.MaintenanceRecordListView.as_view(), name='maintenance_list'),
    path('maintenance/<int:pk>/', views.MaintenanceRecordDetailView.as_view(), name='maintenance_detail'),
    path('maintenance/add/', views.MaintenanceRecordCreateView.as_view(), name='maintenance_add'),
    path('maintenance/<int:pk>/edit/', views.MaintenanceRecordUpdateView.as_view(), name='maintenance_edit'),
    path('maintenance/<int:pk>/delete/', views.MaintenanceRecordDeleteView.as_view(), name='maintenance_delete'),
    
    # 資產類別
    path('categories/', views.AssetCategoryListView.as_view(), name='category_list'),
    path('categories/add/', views.AssetCategoryCreateView.as_view(), name='category_add'),
    path('categories/<int:pk>/edit/', views.AssetCategoryUpdateView.as_view(), name='category_edit'),
    path('categories/<int:pk>/delete/', views.AssetCategoryDeleteView.as_view(), name='category_delete'),
    
    # 報表和統計
    path('reports/', views.AssetReportsView.as_view(), name='reports'),
    path('warranty-alerts/', views.WarrantyAlertsView.as_view(), name='warranty_alerts'),
    path('license-alerts/', views.LicenseAlertsView.as_view(), name='license_alerts'),
    
    # AJAX API
    path('api/asset-search/', views.asset_search_api, name='asset_search_api'),
    path('api/license-search/', views.license_search_api, name='license_search_api'),
] 