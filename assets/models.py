from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal

class Vendor(models.Model):
    """供應商模型"""
    name = models.CharField(max_length=100, verbose_name="供應商名稱")
    contact_person = models.CharField(max_length=50, blank=True, verbose_name="聯絡人")
    phone = models.CharField(max_length=20, blank=True, verbose_name="電話")
    email = models.EmailField(blank=True, verbose_name="電子郵件")
    address = models.TextField(blank=True, verbose_name="地址")
    website = models.URLField(blank=True, verbose_name="網站")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")

    class Meta:
        verbose_name = "供應商"
        verbose_name_plural = "供應商"
        ordering = ['name']

    def __str__(self):
        return self.name

class AssetCategory(models.Model):
    """資產類別模型"""
    name = models.CharField(max_length=50, unique=True, verbose_name="類別名稱")
    description = models.TextField(blank=True, verbose_name="描述")
    depreciation_years = models.IntegerField(default=5, verbose_name="折舊年限")
    
    class Meta:
        verbose_name = "資產類別"
        verbose_name_plural = "資產類別"
        ordering = ['name']

    def __str__(self):
        return self.name

class HardwareAsset(models.Model):
    """硬體資產模型"""
    STATUS_CHOICES = [
        ('active', '使用中'),
        ('inactive', '閒置'),
        ('maintenance', '維修中'),
        ('retired', '已報廢'),
        ('lost', '遺失'),
    ]

    CONDITION_CHOICES = [
        ('excellent', '極佳'),
        ('good', '良好'),
        ('fair', '普通'),
        ('poor', '差'),
        ('broken', '損壞'),
    ]

    # 基本資訊
    asset_tag = models.CharField(max_length=50, unique=True, verbose_name="資產標籤")
    name = models.CharField(max_length=100, verbose_name="資產名稱")
    category = models.CharField(max_length=50, verbose_name="資產類別")
    brand = models.CharField(max_length=50, blank=True, verbose_name="品牌")
    model = models.CharField(max_length=100, blank=True, verbose_name="型號")
    serial_number = models.CharField(max_length=100, blank=True, verbose_name="序號")
    
    # 採購資訊
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="供應商")
    purchase_date = models.DateField(null=True, blank=True, verbose_name="採購日期")
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="採購價格")
    invoice_number = models.CharField(max_length=50, blank=True, verbose_name="發票號碼")
    
    # 保固資訊
    warranty_start_date = models.DateField(null=True, blank=True, verbose_name="保固開始日期")
    warranty_end_date = models.DateField(null=True, blank=True, verbose_name="保固結束日期")
    warranty_provider = models.CharField(max_length=100, blank=True, verbose_name="保固提供商")
    
    # 使用狀態
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="狀態")
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='good', verbose_name="狀況")
    location = models.CharField(max_length=100, blank=True, verbose_name="位置")
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="使用者")
    
    # 規格資訊（JSON格式儲存彈性規格）
    specifications = models.JSONField(default=dict, blank=True, verbose_name="規格")
    
    # 備註
    notes = models.TextField(blank=True, verbose_name="備註")
    
    # 時間戳記
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")

    class Meta:
        verbose_name = "硬體資產"
        verbose_name_plural = "硬體資產"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.asset_tag} - {self.name}"

    @property
    def is_warranty_expired(self):
        """檢查保固是否過期"""
        if self.warranty_end_date:
            return timezone.now().date() > self.warranty_end_date
        return None

    @property
    def warranty_days_remaining(self):
        """保固剩餘天數"""
        if self.warranty_end_date:
            remaining = self.warranty_end_date - timezone.now().date()
            return remaining.days if remaining.days > 0 else 0
        return None

    @property
    def current_value(self):
        """計算當前價值（直線折舊法）"""
        if not self.purchase_price or not self.purchase_date:
            return None
        
        years_since_purchase = (timezone.now().date() - self.purchase_date).days / 365.25
        
        # 嘗試從 AssetCategory 中找到對應的折舊年限，否則使用預設值 5 年
        try:
            asset_category = AssetCategory.objects.get(name=self.category)
            depreciation_years = asset_category.depreciation_years
        except AssetCategory.DoesNotExist:
            depreciation_years = 5  # 預設折舊年限
        
        if years_since_purchase >= depreciation_years:
            return Decimal('0.00')
        
        annual_depreciation = self.purchase_price / depreciation_years
        current_value = self.purchase_price - (annual_depreciation * Decimal(str(years_since_purchase)))
        
        return max(current_value, Decimal('0.00'))

class SoftwareLicense(models.Model):
    """軟體授權模型"""
    LICENSE_TYPE_CHOICES = [
        ('perpetual', '永久授權'),
        ('subscription', '訂閱授權'),
        ('volume', '大量授權'),
        ('oem', 'OEM授權'),
        ('trial', '試用版'),
        ('free', '免費軟體'),
    ]

    STATUS_CHOICES = [
        ('active', '使用中'),
        ('expired', '已過期'),
        ('unused', '未使用'),
        ('retired', '已停用'),
    ]

    # 基本資訊
    software_name = models.CharField(max_length=100, verbose_name="軟體名稱")
    version = models.CharField(max_length=50, blank=True, verbose_name="版本")
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="供應商")
    license_type = models.CharField(max_length=20, choices=LICENSE_TYPE_CHOICES, verbose_name="授權類型")
    
    # 授權資訊
    license_key = models.CharField(max_length=200, blank=True, verbose_name="授權金鑰")
    total_licenses = models.IntegerField(default=1, verbose_name="總授權數")
    used_licenses = models.IntegerField(default=0, verbose_name="已使用授權數")
    
    # 日期資訊
    purchase_date = models.DateField(null=True, blank=True, verbose_name="採購日期")
    start_date = models.DateField(null=True, blank=True, verbose_name="開始日期")
    expiry_date = models.DateField(null=True, blank=True, verbose_name="到期日期")
    
    # 財務資訊
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="採購價格")
    annual_maintenance_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="年度維護費用")
    
    # 狀態
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="狀態")
    
    # 使用者分配
    assigned_users = models.ManyToManyField(User, blank=True, verbose_name="分配用戶")
    
    # 備註
    notes = models.TextField(blank=True, verbose_name="備註")
    
    # 時間戳記
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")

    class Meta:
        verbose_name = "軟體授權"
        verbose_name_plural = "軟體授權"
        ordering = ['-created_at']

    def __str__(self):
        if self.version:
            return f"{self.software_name} ({self.version})"
        return self.software_name

    @property
    def available_licenses(self):
        """可用授權數"""
        return self.total_licenses - self.used_licenses

    @property
    def is_expired(self):
        """檢查是否過期"""
        if self.expiry_date:
            return timezone.now().date() > self.expiry_date
        return False

    @property
    def days_until_expiry(self):
        """到期剩餘天數"""
        if self.expiry_date:
            remaining = self.expiry_date - timezone.now().date()
            return remaining.days if remaining.days > 0 else 0
        return None

class PurchaseRequest(models.Model):
    """採購申請模型"""
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('submitted', '已提交'),
        ('approved', '已批准'),
        ('rejected', '已拒絕'),
        ('purchased', '已採購'),
        ('received', '已收貨'),
        ('cancelled', '已取消'),
    ]

    PRIORITY_CHOICES = [
        ('low', '低'),
        ('medium', '中'),
        ('high', '高'),
        ('urgent', '緊急'),
    ]

    # 基本資訊
    request_number = models.CharField(max_length=20, unique=True, verbose_name="申請單號")
    title = models.CharField(max_length=200, verbose_name="申請標題")
    description = models.TextField(verbose_name="申請描述")
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchase_requests', verbose_name="申請人")
    
    # 申請狀態
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="狀態")
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium', verbose_name="優先級")
    
    # 預算資訊
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="預估費用")
    budget_code = models.CharField(max_length=20, blank=True, verbose_name="預算代碼")
    
    # 審核資訊
    approver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_requests', verbose_name="審核人")
    approval_date = models.DateTimeField(null=True, blank=True, verbose_name="審核日期")
    approval_notes = models.TextField(blank=True, verbose_name="審核備註")
    
    # 採購資訊
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="供應商")
    actual_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="實際費用")
    purchase_date = models.DateField(null=True, blank=True, verbose_name="採購日期")
    expected_delivery_date = models.DateField(null=True, blank=True, verbose_name="預計交貨日期")
    
    # 備註
    notes = models.TextField(blank=True, verbose_name="備註")
    
    # 時間戳記
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")

    class Meta:
        verbose_name = "採購申請"
        verbose_name_plural = "採購申請"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.request_number} - {self.title}"

    def save(self, *args, **kwargs):
        if not self.request_number:
            # 生成申請單號
            year = timezone.now().year
            count = PurchaseRequest.objects.filter(created_at__year=year).count() + 1
            self.request_number = f"PR{year}{count:04d}"
        super().save(*args, **kwargs)

class MaintenanceRecord(models.Model):
    """維修記錄模型"""
    MAINTENANCE_TYPE_CHOICES = [
        ('preventive', '預防性維護'),
        ('corrective', '修復性維護'),
        ('upgrade', '升級'),
        ('inspection', '檢查'),
    ]

    STATUS_CHOICES = [
        ('scheduled', '已排程'),
        ('in_progress', '進行中'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    ]

    # 關聯資產
    asset = models.ForeignKey(HardwareAsset, on_delete=models.CASCADE, related_name='maintenance_records', verbose_name="資產")
    
    # 維修資訊
    maintenance_type = models.CharField(max_length=20, choices=MAINTENANCE_TYPE_CHOICES, verbose_name="維修類型")
    description = models.TextField(verbose_name="維修描述")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled', verbose_name="狀態")
    
    # 時間資訊
    scheduled_date = models.DateTimeField(verbose_name="排程日期")
    started_at = models.DateTimeField(null=True, blank=True, verbose_name="開始時間")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="完成時間")
    
    # 執行資訊
    technician = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="技術人員")
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="外包廠商")
    
    # 費用資訊
    cost = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name="費用")
    
    # 備註
    notes = models.TextField(blank=True, verbose_name="維修備註")
    
    # 時間戳記
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")

    class Meta:
        verbose_name = "維修記錄"
        verbose_name_plural = "維修記錄"
        ordering = ['-scheduled_date']

    def __str__(self):
        return f"{self.asset.name} - {self.get_maintenance_type_display()}"
