from django import forms
from django.core.exceptions import ValidationError
from .models import FirewallRule, SSLCertificate, VPNConnection
import re


class FirewallRuleForm(forms.ModelForm):
    class Meta:
        model = FirewallRule
        fields = ['name', 'description', 'rule_type', 'status', 'priority', 
                 'source_ip', 'source_port', 'destination_ip', 'destination_port', 
                 'protocol', 'direction', 'is_system_rule']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '輸入規則名稱',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '輸入規則說明（選填）'
            }),
            'rule_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'priority': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 9999,
                'value': 100
            }),
            'source_ip': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '來源 IP 位址（留空表示任何 IP）'
            }),
            'source_port': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '來源埠號，如：80, 443, 8000-9000'
            }),
            'destination_ip': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '目標 IP 位址（留空表示任何 IP）'
            }),
            'destination_port': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '目標埠號，如：80, 443, 8000-9000'
            }),
            'protocol': forms.Select(attrs={
                'class': 'form-select'
            }),
            'direction': forms.Select(attrs={
                'class': 'form-select'
            }),
            'is_system_rule': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def clean_source_port(self):
        port = self.cleaned_data.get('source_port')
        if port:
            return self._validate_port_format(port, 'source_port')
        return port
    
    def clean_destination_port(self):
        port = self.cleaned_data.get('destination_port')
        if port:
            return self._validate_port_format(port, 'destination_port')
        return port
    
    def _validate_port_format(self, port_string, field_name):
        """驗證埠號格式"""
        # 允許的格式：80, 80,443, 8000-9000, 80,443,8000-9000
        port_pattern = r'^(\d+(-\d+)?)(,\d+(-\d+)?)*$'
        if not re.match(port_pattern, port_string.replace(' ', '')):
            raise ValidationError(
                f'{field_name} 格式不正確，請使用如：80, 80,443, 8000-9000 的格式'
            )
        
        # 驗證埠號範圍
        parts = port_string.replace(' ', '').split(',')
        for part in parts:
            if '-' in part:
                start, end = part.split('-')
                if int(start) >= int(end):
                    raise ValidationError(f'{field_name} 範圍格式錯誤：{part}')
                if not (1 <= int(start) <= 65535) or not (1 <= int(end) <= 65535):
                    raise ValidationError(f'{field_name} 埠號超出範圍（1-65535）：{part}')
            else:
                if not (1 <= int(part) <= 65535):
                    raise ValidationError(f'{field_name} 埠號超出範圍（1-65535）：{part}')
        
        return port_string
    
    def clean(self):
        cleaned_data = super().clean()
        protocol = cleaned_data.get('protocol')
        source_port = cleaned_data.get('source_port')
        destination_port = cleaned_data.get('destination_port')
        
        # ICMP 協定不需要埠號
        if protocol == 'icmp':
            if source_port or destination_port:
                raise ValidationError('ICMP 協定不需要指定埠號')
        
        return cleaned_data


class SSLCertificateForm(forms.ModelForm):
    class Meta:
        model = SSLCertificate
        fields = ['name', 'domain', 'cert_type', 'issuer', 'serial_number', 
                 'subject', 'san_domains', 'issued_date', 'expires_date', 
                 'certificate_file', 'private_key_file', 'remind_days_before']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '輸入憑證名稱'
            }),
            'domain': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '如：example.com'
            }),
            'cert_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'issuer': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '如：Let\'s Encrypt, DigiCert 等'
            }),
            'serial_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '憑證序號'
            }),
            'subject': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '憑證主體資訊'
            }),
            'san_domains': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': '多個域名請用逗號分隔'
            }),
            'issued_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'expires_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'certificate_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.crt,.pem,.cer'
            }),
            'private_key_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.key,.pem'
            }),
            'remind_days_before': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 365,
                'value': 30
            })
        }
    
    def clean_san_domains(self):
        """處理 SAN 域名字符串轉換為列表"""
        san_domains = self.cleaned_data.get('san_domains')
        if san_domains:
            if isinstance(san_domains, str):
                # 將逗號分隔的字符串轉換為列表
                domains = [domain.strip() for domain in san_domains.split(',') if domain.strip()]
                return domains
        return []


class VPNConnectionForm(forms.ModelForm):
    class Meta:
        model = VPNConnection
        fields = ['name', 'connection_type', 'server_address', 'local_ip', 
                 'remote_ip', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '輸入連線名稱'
            }),
            'connection_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'server_address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '如：vpn.example.com 或 192.168.1.1'
            }),
            'local_ip': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '本地 IP 位址（選填）'
            }),
            'remote_ip': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '遠端 IP 位址（選填）'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        } 