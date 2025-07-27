from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    Vendor, AssetCategory, HardwareAsset, SoftwareLicense, 
    PurchaseRequest, MaintenanceRecord
)

@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ['name', 'contact_person', 'phone', 'email', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'contact_person', 'email']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('基本資訊', {
            'fields': ('name', 'contact_person', 'phone', 'email')
        }),
        ('詳細資訊', {
            'fields': ('address', 'website')
        }),
        ('時間戳記', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(AssetCategory)
class AssetCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'depreciation_years']
    list_filter = ['name']
    search_fields = ['name']

@admin.register(HardwareAsset)
class HardwareAssetAdmin(admin.ModelAdmin):
    list_display = [
        'asset_tag', 'name', 'category', 'brand', 'model', 
        'status', 'condition', 'assigned_to', 'warranty_status'
    ]
    list_filter = [
        'status', 'condition', 'category', 'brand', 
        'purchase_date', 'warranty_end_date'
    ]
    search_fields = [
        'asset_tag', 'name', 'brand', 'model', 'serial_number'
    ]
    readonly_fields = [
        'current_value', 'warranty_days_remaining', 
        'created_at', 'updated_at'
    ]
    date_hierarchy = 'purchase_date'
    
    fieldsets = (
        ('基本資訊', {
            'fields': (
                'asset_tag', 'name', 'category', 
                'brand', 'model', 'serial_number'
            )
        }),
        ('採購資訊', {
            'fields': (
                'vendor', 'purchase_date', 'purchase_price', 
                'invoice_number'
            )
        }),
        ('保固資訊', {
            'fields': (
                'warranty_start_date', 'warranty_end_date', 
                'warranty_provider', 'warranty_days_remaining'
            )
        }),
        ('使用狀態', {
            'fields': (
                'status', 'condition', 'location', 'assigned_to'
            )
        }),
        ('規格與備註', {
            'fields': ('specifications', 'notes'),
            'classes': ('collapse',)
        }),
        ('計算欄位', {
            'fields': ('current_value',),
            'classes': ('collapse',)
        }),
        ('時間戳記', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def warranty_status(self, obj):
        """顯示保固狀態"""
        if obj.warranty_end_date is None:
            return "無保固資訊"
        
        if obj.is_warranty_expired:
            return format_html(
                '<span style="color: red;">已過期</span>'
            )
        elif obj.warranty_days_remaining and obj.warranty_days_remaining <= 30:
            return format_html(
                '<span style="color: orange;">即將到期 ({} 天)</span>',
                obj.warranty_days_remaining
            )
        else:
            return format_html(
                '<span style="color: green;">有效 ({} 天)</span>',
                obj.warranty_days_remaining or 0
            )
    
    warranty_status.short_description = '保固狀態'

@admin.register(SoftwareLicense)
class SoftwareLicenseAdmin(admin.ModelAdmin):
    list_display = [
        'software_name', 'version', 'vendor', 'license_type',
        'license_usage', 'expiry_status', 'status'
    ]
    list_filter = [
        'license_type', 'status', 'vendor', 
        'purchase_date', 'expiry_date'
    ]
    search_fields = ['software_name', 'version', 'license_key']
    readonly_fields = [
        'available_licenses', 'days_until_expiry', 
        'created_at', 'updated_at'
    ]
    filter_horizontal = ['assigned_users']
    date_hierarchy = 'purchase_date'
    
    fieldsets = (
        ('基本資訊', {
            'fields': (
                'software_name', 'version', 'vendor', 'license_type'
            )
        }),
        ('授權資訊', {
            'fields': (
                'license_key', 'total_licenses', 'used_licenses', 
                'available_licenses'
            )
        }),
        ('日期資訊', {
            'fields': (
                'purchase_date', 'start_date', 'expiry_date',
                'days_until_expiry'
            )
        }),
        ('財務資訊', {
            'fields': ('purchase_price', 'annual_maintenance_cost')
        }),
        ('使用者分配', {
            'fields': ('assigned_users', 'status')
        }),
        ('備註', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('時間戳記', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def license_usage(self, obj):
        """顯示授權使用情況"""
        percentage = (obj.used_licenses / obj.total_licenses) * 100 if obj.total_licenses > 0 else 0
        
        if percentage >= 90:
            color = 'red'
        elif percentage >= 70:
            color = 'orange'
        else:
            color = 'green'
            
        return format_html(
            '<span style="color: {};">{}/{} ({:.1f}%)</span>',
            color, obj.used_licenses, obj.total_licenses, percentage
        )
    
    license_usage.short_description = '授權使用率'
    
    def expiry_status(self, obj):
        """顯示到期狀態"""
        if obj.expiry_date is None:
            return "永久授權"
        
        if obj.is_expired:
            return format_html(
                '<span style="color: red;">已過期</span>'
            )
        elif obj.days_until_expiry and obj.days_until_expiry <= 30:
            return format_html(
                '<span style="color: orange;">即將到期 ({} 天)</span>',
                obj.days_until_expiry
            )
        else:
            return format_html(
                '<span style="color: green;">有效 ({} 天)</span>',
                obj.days_until_expiry or 0
            )
    
    expiry_status.short_description = '到期狀態'

@admin.register(PurchaseRequest)
class PurchaseRequestAdmin(admin.ModelAdmin):
    list_display = [
        'request_number', 'title', 'requester', 'status', 
        'priority', 'estimated_cost', 'created_at'
    ]
    list_filter = [
        'status', 'priority', 'created_at', 
        'approval_date', 'purchase_date'
    ]
    search_fields = [
        'request_number', 'title', 'description', 
        'requester__username', 'requester__first_name', 'requester__last_name'
    ]
    readonly_fields = ['request_number', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('基本資訊', {
            'fields': (
                'request_number', 'title', 'description', 
                'requester', 'status', 'priority'
            )
        }),
        ('預算資訊', {
            'fields': ('estimated_cost', 'budget_code')
        }),
        ('審核資訊', {
            'fields': (
                'approver', 'approval_date', 'approval_notes'
            )
        }),
        ('採購資訊', {
            'fields': (
                'vendor', 'actual_cost', 'purchase_date', 
                'expected_delivery_date'
            )
        }),
        ('備註', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('時間戳記', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        """根據狀態動態設定唯讀欄位"""
        readonly_fields = list(self.readonly_fields)
        
        if obj and obj.status in ['approved', 'purchased', 'received']:
            # 已批准後不能修改基本資訊
            readonly_fields.extend([
                'title', 'description', 'estimated_cost', 
                'budget_code', 'priority'
            ])
        
        return readonly_fields

@admin.register(MaintenanceRecord)
class MaintenanceRecordAdmin(admin.ModelAdmin):
    list_display = [
        'asset', 'maintenance_type', 'status', 'scheduled_date',
        'technician', 'cost'
    ]
    list_filter = [
        'maintenance_type', 'status', 'scheduled_date',
        'technician', 'vendor'
    ]
    search_fields = [
        'asset__name', 'asset__asset_tag', 'description',
        'technician__username'
    ]
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'scheduled_date'
    
    fieldsets = (
        ('基本資訊', {
            'fields': (
                'asset', 'maintenance_type', 'description', 'status'
            )
        }),
        ('時間安排', {
            'fields': (
                'scheduled_date', 'started_at', 'completed_at'
            )
        }),
        ('執行資訊', {
            'fields': ('technician', 'vendor', 'cost')
        }),
        ('備註', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('時間戳記', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

# 自訂管理介面標題
admin.site.site_header = 'OpenOA Manager'
admin.site.site_title = 'OpenOA Manager'
admin.site.index_title = '管理系統'
