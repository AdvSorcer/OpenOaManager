from django import forms
from django.contrib.auth.models import User
from .models import (
    Vendor, AssetCategory, HardwareAsset, SoftwareLicense, 
    PurchaseRequest, MaintenanceRecord
)

class VendorForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = ['name', 'contact_person', 'phone', 'email', 'address', 'website']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
        }

class AssetCategoryForm(forms.ModelForm):
    class Meta:
        model = AssetCategory
        fields = ['name', 'description', 'depreciation_years']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '例如：桌上型電腦、筆記型電腦、伺服器等'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'depreciation_years': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class HardwareAssetForm(forms.ModelForm):
    class Meta:
        model = HardwareAsset
        fields = [
            'asset_tag', 'name', 'category', 'brand', 'model', 'serial_number',
            'vendor', 'purchase_date', 'purchase_price', 'invoice_number',
            'warranty_start_date', 'warranty_end_date', 'warranty_provider',
            'status', 'condition', 'location', 'assigned_to', 'specifications', 'notes'
        ]
        widgets = {
            'asset_tag': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '例如：桌上型電腦、筆記型電腦、伺服器等'}),
            'brand': forms.TextInput(attrs={'class': 'form-control'}),
            'model': forms.TextInput(attrs={'class': 'form-control'}),
            'serial_number': forms.TextInput(attrs={'class': 'form-control'}),
            'vendor': forms.Select(attrs={'class': 'form-control'}),
            'purchase_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'purchase_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'invoice_number': forms.TextInput(attrs={'class': 'form-control'}),
            'warranty_start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'warranty_end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'warranty_provider': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'condition': forms.Select(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'assigned_to': forms.Select(attrs={'class': 'form-control'}),
            'specifications': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': '請輸入JSON格式的規格資訊'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_to'].queryset = User.objects.filter(is_active=True)
        self.fields['assigned_to'].empty_label = "未分配"

class SoftwareLicenseForm(forms.ModelForm):
    class Meta:
        model = SoftwareLicense
        fields = [
            'software_name', 'version', 'vendor', 'license_type',
            'license_key', 'total_licenses', 'used_licenses',
            'purchase_date', 'start_date', 'expiry_date',
            'purchase_price', 'annual_maintenance_cost',
            'status', 'assigned_users', 'notes'
        ]
        widgets = {
            'software_name': forms.TextInput(attrs={'class': 'form-control'}),
            'version': forms.TextInput(attrs={'class': 'form-control'}),
            'vendor': forms.Select(attrs={'class': 'form-control'}),
            'license_type': forms.Select(attrs={'class': 'form-control'}),
            'license_key': forms.TextInput(attrs={'class': 'form-control'}),
            'total_licenses': forms.NumberInput(attrs={'class': 'form-control'}),
            'used_licenses': forms.NumberInput(attrs={'class': 'form-control'}),
            'purchase_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'purchase_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'annual_maintenance_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'assigned_users': forms.SelectMultiple(attrs={'class': 'form-control', 'size': '5'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_users'].queryset = User.objects.filter(is_active=True)

class PurchaseRequestForm(forms.ModelForm):
    class Meta:
        model = PurchaseRequest
        fields = [
            'title', 'description', 'priority', 'estimated_cost', 
            'budget_code', 'notes'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'estimated_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'budget_code': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class PurchaseRequestApprovalForm(forms.ModelForm):
    """採購申請審核表單"""
    class Meta:
        model = PurchaseRequest
        fields = ['status', 'approval_notes', 'vendor', 'actual_cost', 'purchase_date', 'expected_delivery_date']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'approval_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'vendor': forms.Select(attrs={'class': 'form-control'}),
            'actual_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'purchase_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'expected_delivery_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

class MaintenanceRecordForm(forms.ModelForm):
    class Meta:
        model = MaintenanceRecord
        fields = [
            'asset', 'maintenance_type', 'description', 'status',
            'scheduled_date', 'started_at', 'completed_at',
            'technician', 'vendor', 'cost', 'notes'
        ]
        widgets = {
            'asset': forms.Select(attrs={'class': 'form-control'}),
            'maintenance_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'scheduled_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'started_at': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'completed_at': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'technician': forms.Select(attrs={'class': 'form-control'}),
            'vendor': forms.Select(attrs={'class': 'form-control'}),
            'cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['technician'].queryset = User.objects.filter(is_active=True)
        self.fields['technician'].empty_label = "未指派"

# 搜尋表單
class AssetSearchForm(forms.Form):
    search = forms.CharField(
        max_length=100, 
        required=False,
        label='搜尋關鍵字',
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': '搜尋資產標籤、名稱、品牌或型號...'
        })
    )
    category = forms.CharField(
        max_length=50,
        required=False,
        label='資產類別',
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': '輸入類別名稱進行篩選...'
        })
    )
    status = forms.ChoiceField(
        choices=[('', '所有狀態')] + HardwareAsset.STATUS_CHOICES,
        required=False,
        label='資產狀態',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    vendor = forms.ModelChoiceField(
        queryset=Vendor.objects.all(),
        required=False,
        empty_label="所有供應商",
        label='供應商',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class LicenseSearchForm(forms.Form):
    search = forms.CharField(
        max_length=100, 
        required=False,
        label='搜尋關鍵字',
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': '搜尋軟體名稱或版本...'
        })
    )
    license_type = forms.ChoiceField(
        choices=[('', '所有授權類型')] + SoftwareLicense.LICENSE_TYPE_CHOICES,
        required=False,
        label='授權類型',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    status = forms.ChoiceField(
        choices=[('', '所有狀態')] + SoftwareLicense.STATUS_CHOICES,
        required=False,
        label='授權狀態',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    expiring_soon = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="即將到期（30天內）"
    ) 