from django.db import models
from django.contrib.auth.models import User
from django.core.validators import validate_ipv4_address, validate_ipv6_address
from django.core.exceptions import ValidationError


class FirewallRule(models.Model):
    """防火牆規則模型"""
    
    RULE_TYPE_CHOICES = [
        ('allow', '允許'),
        ('deny', '拒絕'),
        ('drop', '丟棄'),
    ]
    
    PROTOCOL_CHOICES = [
        ('tcp', 'TCP'),
        ('udp', 'UDP'),
        ('icmp', 'ICMP'),
        ('any', '任何協定'),
    ]
    
    DIRECTION_CHOICES = [
        ('inbound', '入站'),
        ('outbound', '出站'),
        ('both', '雙向'),
    ]
    
    STATUS_CHOICES = [
        ('active', '啟用'),
        ('inactive', '停用'),
        ('testing', '測試中'),
    ]
    
    # 基本資訊
    name = models.CharField('規則名稱', max_length=100)
    description = models.TextField('說明', blank=True)
    rule_type = models.CharField('動作', max_length=10, choices=RULE_TYPE_CHOICES, default='allow')
    status = models.CharField('狀態', max_length=10, choices=STATUS_CHOICES, default='active')
    priority = models.IntegerField('優先級', default=100, help_text='數字越小優先級越高')
    
    # 網路設定
    source_ip = models.GenericIPAddressField('來源IP', blank=True, null=True, help_text='空白表示任何IP')
    source_port = models.CharField('來源埠', max_length=20, blank=True, help_text='可使用範圍如 1000-2000 或逗號分隔')
    destination_ip = models.GenericIPAddressField('目標IP', blank=True, null=True, help_text='空白表示任何IP')
    destination_port = models.CharField('目標埠', max_length=20, blank=True, help_text='可使用範圍如 80,443,8000-9000')
    protocol = models.CharField('協定', max_length=10, choices=PROTOCOL_CHOICES, default='any')
    direction = models.CharField('方向', max_length=10, choices=DIRECTION_CHOICES, default='inbound')
    
    # 管理資訊
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='建立者')
    created_at = models.DateTimeField('建立時間', auto_now_add=True)
    updated_at = models.DateTimeField('更新時間', auto_now=True)
    is_system_rule = models.BooleanField('系統規則', default=False, help_text='系統規則無法刪除')
    
    # 統計資訊
    hit_count = models.PositiveIntegerField('命中次數', default=0)
    last_hit = models.DateTimeField('最後命中時間', blank=True, null=True)
    
    class Meta:
        verbose_name = '防火牆規則'
        verbose_name_plural = '防火牆規則'
        ordering = ['priority', '-created_at']
        indexes = [
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['source_ip']),
            models.Index(fields=['destination_ip']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_rule_type_display()})"
    
    def clean(self):
        """驗證規則的合理性"""
        if self.protocol == 'icmp' and (self.source_port or self.destination_port):
            raise ValidationError('ICMP 協定不需要指定埠號')
    
    def get_rule_summary(self):
        """取得規則摘要"""
        source = self.source_ip or '任何IP'
        dest = self.destination_ip or '任何IP'
        return f"{source} -> {dest} ({self.protocol.upper()})"


class FirewallRuleLog(models.Model):
    """防火牆規則日誌"""
    
    LOG_TYPE_CHOICES = [
        ('hit', '命中'),
        ('block', '阻擋'),
        ('allow', '允許'),
    ]
    
    rule = models.ForeignKey(FirewallRule, on_delete=models.CASCADE, verbose_name='相關規則')
    log_type = models.CharField('日誌類型', max_length=10, choices=LOG_TYPE_CHOICES)
    source_ip = models.GenericIPAddressField('來源IP')
    destination_ip = models.GenericIPAddressField('目標IP')
    source_port = models.PositiveIntegerField('來源埠', blank=True, null=True)
    destination_port = models.PositiveIntegerField('目標埠', blank=True, null=True)
    protocol = models.CharField('協定', max_length=10)
    packet_size = models.PositiveIntegerField('封包大小', blank=True, null=True)
    timestamp = models.DateTimeField('時間', auto_now_add=True)
    
    class Meta:
        verbose_name = '防火牆日誌'
        verbose_name_plural = '防火牆日誌'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['rule', '-timestamp']),
            models.Index(fields=['source_ip', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.source_ip} -> {self.destination_ip} ({self.timestamp})"


class SSLCertificate(models.Model):
    """SSL憑證管理"""
    
    CERT_TYPE_CHOICES = [
        ('domain', '網域憑證'),
        ('wildcard', '萬用憑證'),
        ('ev', 'EV憑證'),
        ('ov', 'OV憑證'),
        ('dv', 'DV憑證'),
    ]
    
    STATUS_CHOICES = [
        ('valid', '有效'),
        ('expired', '已過期'),
        ('expiring', '即將過期'),
        ('revoked', '已撤銷'),
    ]
    
    name = models.CharField('憑證名稱', max_length=100)
    domain = models.CharField('網域名稱', max_length=255)
    cert_type = models.CharField('憑證類型', max_length=20, choices=CERT_TYPE_CHOICES)
    issuer = models.CharField('發行機構', max_length=100)
    
    # 憑證資訊
    serial_number = models.CharField('序號', max_length=100, unique=True)
    subject = models.TextField('主體資訊')
    san_domains = models.JSONField('SAN網域', default=list, blank=True, help_text='主體別名中的其他網域')
    
    # 時間相關
    issued_date = models.DateTimeField('發行日期')
    expires_date = models.DateTimeField('到期日期')
    status = models.CharField('狀態', max_length=20, choices=STATUS_CHOICES, default='valid')
    
    # 檔案
    certificate_file = models.FileField('憑證檔案', upload_to='certificates/', blank=True)
    private_key_file = models.FileField('私鑰檔案', upload_to='private_keys/', blank=True)
    
    # 管理資訊
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='建立者')
    created_at = models.DateTimeField('建立時間', auto_now_add=True)
    updated_at = models.DateTimeField('更新時間', auto_now=True)
    
    # 提醒設定
    remind_days_before = models.PositiveIntegerField('提前提醒天數', default=30)
    last_reminder_sent = models.DateTimeField('最後提醒時間', blank=True, null=True)
    
    class Meta:
        verbose_name = 'SSL憑證'
        verbose_name_plural = 'SSL憑證'
        ordering = ['expires_date']
        indexes = [
            models.Index(fields=['expires_date']),
            models.Index(fields=['domain']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.domain} - {self.name}"
    
    @property
    def days_until_expiry(self):
        """計算距離到期的天數"""
        if not self.expires_date:
            return None
        from django.utils import timezone
        delta = self.expires_date - timezone.now()
        return delta.days
    
    def is_expiring_soon(self):
        """檢查是否即將到期"""
        days = self.days_until_expiry
        if days is None:
            return False
        return 0 <= days <= self.remind_days_before
    
    def update_status(self, save=True):
        """更新憑證狀態"""
        if not self.expires_date:
            self.status = 'valid'  # 如果沒有到期日期，默認為有效
            if save:
                self.save(update_fields=['status'])
            return
            
        from django.utils import timezone
        now = timezone.now()
        
        if self.expires_date < now:
            self.status = 'expired'
        elif self.is_expiring_soon():
            self.status = 'expiring'
        else:
            self.status = 'valid'
            
        if save:
            self.save(update_fields=['status'])


class VPNConnection(models.Model):
    """VPN連線管理"""
    
    CONNECTION_TYPE_CHOICES = [
        ('openvpn', 'OpenVPN'),
        ('ipsec', 'IPSec'),
        ('pptp', 'PPTP'),
        ('l2tp', 'L2TP'),
        ('wireguard', 'WireGuard'),
    ]
    
    STATUS_CHOICES = [
        ('connected', '已連線'),
        ('disconnected', '未連線'),
        ('connecting', '連線中'),
        ('error', '錯誤'),
    ]
    
    name = models.CharField('連線名稱', max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='使用者')
    connection_type = models.CharField('VPN類型', max_length=20, choices=CONNECTION_TYPE_CHOICES)
    server_address = models.CharField('伺服器位址', max_length=255)
    
    # 連線資訊
    local_ip = models.GenericIPAddressField('本地IP', blank=True, null=True)
    remote_ip = models.GenericIPAddressField('遠端IP', blank=True, null=True)
    status = models.CharField('狀態', max_length=20, choices=STATUS_CHOICES, default='disconnected')
    
    # 統計資訊
    connected_at = models.DateTimeField('連線時間', blank=True, null=True)
    disconnected_at = models.DateTimeField('斷線時間', blank=True, null=True)
    bytes_sent = models.BigIntegerField('傳送位元組', default=0)
    bytes_received = models.BigIntegerField('接收位元組', default=0)
    
    # 管理資訊
    created_at = models.DateTimeField('建立時間', auto_now_add=True)
    updated_at = models.DateTimeField('更新時間', auto_now=True)
    is_active = models.BooleanField('啟用', default=True)
    
    class Meta:
        verbose_name = 'VPN連線'
        verbose_name_plural = 'VPN連線'
        ordering = ['-connected_at', 'name']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['-connected_at']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.user.username}"
    
    @property
    def connection_duration(self):
        """計算連線時長"""
        if self.connected_at and self.status == 'connected':
            from django.utils import timezone
            return timezone.now() - self.connected_at
        elif self.connected_at and self.disconnected_at:
            return self.disconnected_at - self.connected_at
        return None
    
    def get_data_usage(self):
        """取得數據使用量"""
        total_bytes = self.bytes_sent + self.bytes_received
        if total_bytes < 1024:
            return f"{total_bytes} B"
        elif total_bytes < 1024 * 1024:
            return f"{total_bytes / 1024:.1f} KB"
        elif total_bytes < 1024 * 1024 * 1024:
            return f"{total_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{total_bytes / (1024 * 1024 * 1024):.1f} GB"
