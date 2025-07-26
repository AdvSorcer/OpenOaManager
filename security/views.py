from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .models import FirewallRule, SSLCertificate, VPNConnection
from .forms import FirewallRuleForm, SSLCertificateForm, VPNConnectionForm


# ==================== 防火牆規則管理 ====================

@login_required
def firewall_list(request):
    """防火牆規則列表"""
    rules = FirewallRule.objects.all()
    
    # 搜索功能
    search = request.GET.get('search', '')
    if search:
        rules = rules.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search) |
            Q(source_ip__icontains=search) |
            Q(destination_ip__icontains=search)
        )
    
    # 篩選功能
    status_filter = request.GET.get('status', '')
    if status_filter:
        rules = rules.filter(status=status_filter)
    
    protocol_filter = request.GET.get('protocol', '')
    if protocol_filter:
        rules = rules.filter(protocol=protocol_filter)
    
    rule_type_filter = request.GET.get('rule_type', '')
    if rule_type_filter:
        rules = rules.filter(rule_type=rule_type_filter)
    
    # 排序
    sort_by = request.GET.get('sort', 'priority')
    if sort_by == 'name':
        rules = rules.order_by('name')
    elif sort_by == 'created_at':
        rules = rules.order_by('-created_at')
    elif sort_by == 'hit_count':
        rules = rules.order_by('-hit_count')
    else:
        rules = rules.order_by('priority', '-created_at')
    
    # 分頁
    paginator = Paginator(rules, 20)  # 每頁20條記錄
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # 獲取篩選選項
    status_choices = FirewallRule.STATUS_CHOICES
    protocol_choices = FirewallRule.PROTOCOL_CHOICES
    rule_type_choices = FirewallRule.RULE_TYPE_CHOICES
    
    context = {
        'page_obj': page_obj,
        'search': search,
        'status_filter': status_filter,
        'protocol_filter': protocol_filter,
        'rule_type_filter': rule_type_filter,
        'sort_by': sort_by,
        'status_choices': status_choices,
        'protocol_choices': protocol_choices,
        'rule_type_choices': rule_type_choices,
    }
    
    return render(request, 'security/firewall/list.html', context)


@login_required
def firewall_add(request):
    """新增防火牆規則"""
    if request.method == 'POST':
        form = FirewallRuleForm(request.POST)
        if form.is_valid():
            rule = form.save(commit=False)
            rule.created_by = request.user
            rule.save()
            messages.success(request, f'防火牆規則「{rule.name}」已成功建立！')
            return redirect('security:firewall_detail', pk=rule.pk)
    else:
        form = FirewallRuleForm()
    
    context = {
        'form': form,
        'title': '新增防火牆規則',
        'submit_text': '建立規則'
    }
    return render(request, 'security/firewall/form.html', context)


@login_required
def firewall_detail(request, pk):
    """防火牆規則詳細資訊"""
    rule = get_object_or_404(FirewallRule, pk=pk)
    
    # 獲取相關日誌（最近10條）
    recent_logs = rule.firewallrulelog_set.all()[:10]
    
    context = {
        'rule': rule,
        'recent_logs': recent_logs,
    }
    return render(request, 'security/firewall/detail.html', context)


@login_required
def firewall_edit(request, pk):
    """編輯防火牆規則"""
    rule = get_object_or_404(FirewallRule, pk=pk)
    
    # 檢查權限：系統規則只有超級用戶可以編輯
    if rule.is_system_rule and not request.user.is_superuser:
        messages.error(request, '系統規則只能由管理員編輯！')
        return redirect('security:firewall_detail', pk=rule.pk)
    
    if request.method == 'POST':
        form = FirewallRuleForm(request.POST, instance=rule)
        if form.is_valid():
            form.save()
            messages.success(request, f'防火牆規則「{rule.name}」已成功更新！')
            return redirect('security:firewall_detail', pk=rule.pk)
    else:
        form = FirewallRuleForm(instance=rule)
    
    context = {
        'form': form,
        'rule': rule,
        'title': f'編輯防火牆規則 - {rule.name}',
        'submit_text': '更新規則'
    }
    return render(request, 'security/firewall/form.html', context)


@login_required
@require_POST
def firewall_delete(request, pk):
    """刪除防火牆規則"""
    rule = get_object_or_404(FirewallRule, pk=pk)
    
    # 檢查權限：系統規則不能刪除
    if rule.is_system_rule:
        messages.error(request, '系統規則不能刪除！')
        return redirect('security:firewall_detail', pk=rule.pk)
    
    rule_name = rule.name
    rule.delete()
    messages.success(request, f'防火牆規則「{rule_name}」已成功刪除！')
    return redirect('security:firewall_list')


# ==================== SSL 憑證管理 ====================

@login_required
def ssl_list(request):
    """SSL 憑證列表"""
    certificates = SSLCertificate.objects.all()
    
    # 搜索功能
    search = request.GET.get('search', '')
    if search:
        certificates = certificates.filter(
            Q(name__icontains=search) |
            Q(domain__icontains=search) |
            Q(issuer__icontains=search) |
            Q(serial_number__icontains=search)
        )
    
    # 篩選功能
    status_filter = request.GET.get('status', '')
    if status_filter:
        certificates = certificates.filter(status=status_filter)
    
    cert_type_filter = request.GET.get('cert_type', '')
    if cert_type_filter:
        certificates = certificates.filter(cert_type=cert_type_filter)
    
    # 排序
    sort_by = request.GET.get('sort', 'expires_date')
    if sort_by == 'name':
        certificates = certificates.order_by('name')
    elif sort_by == 'domain':
        certificates = certificates.order_by('domain')
    elif sort_by == 'created_at':
        certificates = certificates.order_by('-created_at')
    else:
        certificates = certificates.order_by('expires_date')
    
    # 分頁
    paginator = Paginator(certificates, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # 獲取篩選選項
    status_choices = SSLCertificate.STATUS_CHOICES
    cert_type_choices = SSLCertificate.CERT_TYPE_CHOICES
    
    context = {
        'page_obj': page_obj,
        'search': search,
        'status_filter': status_filter,
        'cert_type_filter': cert_type_filter,
        'sort_by': sort_by,
        'status_choices': status_choices,
        'cert_type_choices': cert_type_choices,
    }
    
    return render(request, 'security/ssl/list.html', context)


@login_required
def ssl_add(request):
    """新增 SSL 憑證"""
    if request.method == 'POST':
        form = SSLCertificateForm(request.POST, request.FILES)
        if form.is_valid():
            cert = form.save(commit=False)
            cert.created_by = request.user
            cert.save()
            messages.success(request, f'SSL 憑證「{cert.name}」已成功建立！')
            return redirect('security:ssl_detail', pk=cert.pk)
    else:
        form = SSLCertificateForm()
    
    context = {
        'form': form,
        'title': '新增 SSL 憑證',
        'submit_text': '建立憑證'
    }
    return render(request, 'security/ssl/form.html', context)


@login_required
def ssl_detail(request, pk):
    """SSL 憑證詳細資訊"""
    certificate = get_object_or_404(SSLCertificate, pk=pk)
    
    context = {
        'certificate': certificate,
    }
    return render(request, 'security/ssl/detail.html', context)


@login_required
def ssl_edit(request, pk):
    """編輯 SSL 憑證"""
    certificate = get_object_or_404(SSLCertificate, pk=pk)
    
    if request.method == 'POST':
        form = SSLCertificateForm(request.POST, request.FILES, instance=certificate)
        if form.is_valid():
            form.save()
            messages.success(request, f'SSL 憑證「{certificate.name}」已成功更新！')
            return redirect('security:ssl_detail', pk=certificate.pk)
    else:
        form = SSLCertificateForm(instance=certificate)
    
    context = {
        'form': form,
        'certificate': certificate,
        'title': f'編輯 SSL 憑證 - {certificate.name}',
        'submit_text': '更新憑證'
    }
    return render(request, 'security/ssl/form.html', context)


@login_required
@require_POST
def ssl_delete(request, pk):
    """刪除 SSL 憑證"""
    certificate = get_object_or_404(SSLCertificate, pk=pk)
    
    cert_name = certificate.name
    certificate.delete()
    messages.success(request, f'SSL 憑證「{cert_name}」已成功刪除！')
    return redirect('security:ssl_list')


# ==================== VPN 連線管理 ====================

@login_required
def vpn_list(request):
    """VPN 連線列表"""
    connections = VPNConnection.objects.all()
    
    # 搜索功能
    search = request.GET.get('search', '')
    if search:
        connections = connections.filter(
            Q(name__icontains=search) |
            Q(server_address__icontains=search) |
            Q(user__username__icontains=search)
        )
    
    # 篩選功能
    status_filter = request.GET.get('status', '')
    if status_filter:
        connections = connections.filter(status=status_filter)
    
    type_filter = request.GET.get('connection_type', '')
    if type_filter:
        connections = connections.filter(connection_type=type_filter)
    
    # 排序
    sort_by = request.GET.get('sort', '-connected_at')
    if sort_by == 'name':
        connections = connections.order_by('name')
    elif sort_by == 'user':
        connections = connections.order_by('user__username')
    elif sort_by == 'created_at':
        connections = connections.order_by('-created_at')
    else:
        connections = connections.order_by('-connected_at', 'name')
    
    # 分頁
    paginator = Paginator(connections, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # 獲取篩選選項
    status_choices = VPNConnection.STATUS_CHOICES
    type_choices = VPNConnection.CONNECTION_TYPE_CHOICES
    
    context = {
        'page_obj': page_obj,
        'search': search,
        'status_filter': status_filter,
        'type_filter': type_filter,
        'sort_by': sort_by,
        'status_choices': status_choices,
        'type_choices': type_choices,
    }
    
    return render(request, 'security/vpn/list.html', context)


@login_required
def vpn_add(request):
    """新增 VPN 連線"""
    if request.method == 'POST':
        form = VPNConnectionForm(request.POST)
        if form.is_valid():
            connection = form.save(commit=False)
            connection.user = request.user
            connection.save()
            messages.success(request, f'VPN 連線「{connection.name}」已成功建立！')
            return redirect('security:vpn_detail', pk=connection.pk)
    else:
        form = VPNConnectionForm()
    
    context = {
        'form': form,
        'title': '新增 VPN 連線',
        'submit_text': '建立連線'
    }
    return render(request, 'security/vpn/form.html', context)


@login_required
def vpn_detail(request, pk):
    """VPN 連線詳細資訊"""
    connection = get_object_or_404(VPNConnection, pk=pk)
    
    context = {
        'connection': connection,
    }
    return render(request, 'security/vpn/detail.html', context)


@login_required
@require_POST
def vpn_delete(request, pk):
    """刪除 VPN 連線"""
    connection = get_object_or_404(VPNConnection, pk=pk)
    
    conn_name = connection.name
    connection.delete()
    messages.success(request, f'VPN 連線「{conn_name}」已成功刪除！')
    return redirect('security:vpn_list')
