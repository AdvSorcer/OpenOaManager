from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import FirewallRule, FirewallRuleLog, SSLCertificate, VPNConnection


@admin.register(FirewallRule)
class FirewallRuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'rule_type', 'status', 'priority', 'protocol', 'direction', 'get_rule_summary', 'hit_count', 'created_at']
    list_filter = ['rule_type', 'status', 'protocol', 'direction', 'is_system_rule', 'created_at']
    search_fields = ['name', 'description', 'source_ip', 'destination_ip']
    readonly_fields = ['hit_count', 'last_hit', 'created_at', 'updated_at']
    
    fieldsets = (
        ('基本資訊', {
            'fields': ('name', 'description', 'rule_type', 'status', 'priority', 'is_system_rule')
        }),
        ('網路設定', {
            'fields': ('source_ip', 'source_port', 'destination_ip', 'destination_port', 'protocol', 'direction')
        }),
        ('統計資訊', {
            'fields': ('hit_count', 'last_hit'),
            'classes': ('collapse',)
        }),
        ('管理資訊', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
            # 新建物件時，先更新狀態（不保存），然後一次性保存
            obj.update_status(save=False)
            super().save_model(request, obj, form, change)
        else:
            # 編輯現有物件時，先保存再更新狀態
            super().save_model(request, obj, form, change)
            obj.update_status()
    
    def get_rule_summary(self, obj):
        return obj.get_rule_summary()
    get_rule_summary.short_description = '規則摘要'
    
    actions = ['enable_rules', 'disable_rules']
    
    def enable_rules(self, request, queryset):
        updated = queryset.update(status='active')
        self.message_user(request, f'已啟用 {updated} 條規則')
    enable_rules.short_description = '啟用選中的規則'
    
    def disable_rules(self, request, queryset):
        updated = queryset.update(status='inactive')
        self.message_user(request, f'已停用 {updated} 條規則')
    disable_rules.short_description = '停用選中的規則'


@admin.register(FirewallRuleLog)
class FirewallRuleLogAdmin(admin.ModelAdmin):
    list_display = ['rule', 'log_type', 'source_ip', 'destination_ip', 'source_port', 'destination_port', 'protocol', 'timestamp']
    list_filter = ['log_type', 'protocol', 'timestamp']
    search_fields = ['source_ip', 'destination_ip', 'rule__name']
    readonly_fields = ['rule', 'log_type', 'source_ip', 'destination_ip', 'source_port', 'destination_port', 'protocol', 'packet_size', 'timestamp']
    date_hierarchy = 'timestamp'
    
    def has_add_permission(self, request):
        return False  # 日誌只能查看，不能新增
    
    def has_change_permission(self, request, obj=None):
        return False  # 日誌不能修改
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser  # 只有超級用戶可以刪除日誌


@admin.register(SSLCertificate)
class SSLCertificateAdmin(admin.ModelAdmin):
    list_display = ['name', 'domain', 'cert_type', 'status', 'issuer', 'expires_date', 'days_until_expiry_display', 'created_at']
    list_filter = ['cert_type', 'status', 'issuer', 'expires_date']
    search_fields = ['name', 'domain', 'issuer', 'serial_number']
    readonly_fields = ['created_at', 'updated_at', 'days_until_expiry_display']
    
    fieldsets = (
        ('基本資訊', {
            'fields': ('name', 'domain', 'cert_type', 'issuer', 'status')
        }),
        ('憑證詳細資訊', {
            'fields': ('serial_number', 'subject', 'san_domains')
        }),
        ('時間資訊', {
            'fields': ('issued_date', 'expires_date', 'days_until_expiry_display')
        }),
        ('檔案', {
            'fields': ('certificate_file', 'private_key_file'),
            'classes': ('collapse',)
        }),
        ('提醒設定', {
            'fields': ('remind_days_before', 'last_reminder_sent'),
            'classes': ('collapse',)
        }),
        ('管理資訊', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
        obj.update_status()  # 在物件已保存後更新狀態
    
    def days_until_expiry_display(self, obj):
        days = obj.days_until_expiry
        if days is None:
            return format_html('<span style="color: gray;">尚未設定到期日</span>')
        elif days < 0:
            return format_html('<span style="color: red;">已過期 {} 天</span>', abs(days))
        elif days <= obj.remind_days_before:
            return format_html('<span style="color: orange;">{} 天後到期</span>', days)
        else:
            return format_html('<span style="color: green;">{} 天後到期</span>', days)
    days_until_expiry_display.short_description = '到期狀態'
    
    actions = ['update_certificate_status', 'send_expiry_reminder']
    
    def update_certificate_status(self, request, queryset):
        for cert in queryset:
            cert.update_status()
        self.message_user(request, f'已更新 {queryset.count()} 個憑證的狀態')
    update_certificate_status.short_description = '更新憑證狀態'
    
    def send_expiry_reminder(self, request, queryset):
        # 這裡可以實作發送提醒郵件的邏輯
        expiring_certs = [cert for cert in queryset if cert.is_expiring_soon()]
        self.message_user(request, f'已發送 {len(expiring_certs)} 個即將到期憑證的提醒')
    send_expiry_reminder.short_description = '發送到期提醒'


@admin.register(VPNConnection)
class VPNConnectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'connection_type', 'status', 'server_address', 'connected_at', 'connection_duration_display', 'data_usage_display']
    list_filter = ['connection_type', 'status', 'is_active', 'connected_at']
    search_fields = ['name', 'user__username', 'server_address', 'local_ip', 'remote_ip']
    readonly_fields = ['connected_at', 'disconnected_at', 'bytes_sent', 'bytes_received', 'created_at', 'updated_at', 'connection_duration_display', 'data_usage_display']
    
    fieldsets = (
        ('基本資訊', {
            'fields': ('name', 'user', 'connection_type', 'server_address', 'is_active')
        }),
        ('連線狀態', {
            'fields': ('status', 'local_ip', 'remote_ip')
        }),
        ('連線統計', {
            'fields': ('connected_at', 'disconnected_at', 'connection_duration_display', 'bytes_sent', 'bytes_received', 'data_usage_display'),
            'classes': ('collapse',)
        }),
        ('管理資訊', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def connection_duration_display(self, obj):
        duration = obj.connection_duration
        if duration:
            hours, remainder = divmod(duration.total_seconds(), 3600)
            minutes, seconds = divmod(remainder, 60)
            return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
        return "-"
    connection_duration_display.short_description = '連線時長'
    
    def data_usage_display(self, obj):
        return obj.get_data_usage()
    data_usage_display.short_description = '數據用量'
    
    actions = ['disconnect_vpn', 'reset_statistics']
    
    def disconnect_vpn(self, request, queryset):
        updated = queryset.filter(status='connected').update(
            status='disconnected',
            disconnected_at=timezone.now()
        )
        self.message_user(request, f'已斷開 {updated} 個 VPN 連線')
    disconnect_vpn.short_description = '斷開選中的 VPN 連線'
    
    def reset_statistics(self, request, queryset):
        updated = queryset.update(bytes_sent=0, bytes_received=0)
        self.message_user(request, f'已重置 {updated} 個連線的統計資料')
    reset_statistics.short_description = '重置統計資料'
