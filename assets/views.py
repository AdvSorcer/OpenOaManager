from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
)
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Count, Sum
from django.utils import timezone
from datetime import timedelta
from .models import (
    Vendor, AssetCategory, HardwareAsset, SoftwareLicense, 
    PurchaseRequest, MaintenanceRecord
)
from .forms import (
    VendorForm, AssetCategoryForm, HardwareAssetForm, SoftwareLicenseForm,
    PurchaseRequestForm, PurchaseRequestApprovalForm, MaintenanceRecordForm,
    AssetSearchForm, LicenseSearchForm
)


# 硬體資產視圖
class HardwareAssetListView(LoginRequiredMixin, ListView):
    model = HardwareAsset
    template_name = 'assets/hardware/list.html'
    context_object_name = 'assets'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = HardwareAsset.objects.select_related('vendor', 'assigned_to')
        form = AssetSearchForm(self.request.GET)
        
        if form.is_valid():
            search = form.cleaned_data.get('search')
            category = form.cleaned_data.get('category')
            status = form.cleaned_data.get('status')
            vendor = form.cleaned_data.get('vendor')
            
            if search:
                queryset = queryset.filter(
                    Q(asset_tag__icontains=search) |
                    Q(name__icontains=search) |
                    Q(brand__icontains=search) |
                    Q(model__icontains=search)
                )
            
            if category:
                queryset = queryset.filter(category__icontains=category)
                
            if status:
                queryset = queryset.filter(status=status)
                
            if vendor:
                queryset = queryset.filter(vendor=vendor)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = AssetSearchForm(self.request.GET)
        return context

class HardwareAssetDetailView(LoginRequiredMixin, DetailView):
    model = HardwareAsset
    template_name = 'assets/hardware/detail.html'
    context_object_name = 'asset'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 取得維修記錄
        context['maintenance_records'] = self.object.maintenance_records.order_by('-scheduled_date')
        return context

class HardwareAssetCreateView(LoginRequiredMixin, CreateView):
    model = HardwareAsset
    form_class = HardwareAssetForm
    template_name = 'assets/hardware/form.html'
    success_url = reverse_lazy('assets:hardware_list')
    
    def form_valid(self, form):
        messages.success(self.request, '硬體資產已成功新增！')
        return super().form_valid(form)

class HardwareAssetUpdateView(LoginRequiredMixin, UpdateView):
    model = HardwareAsset
    form_class = HardwareAssetForm
    template_name = 'assets/hardware/form.html'
    
    def get_success_url(self):
        return reverse_lazy('assets:hardware_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, '硬體資產已成功更新！')
        return super().form_valid(form)

class HardwareAssetDeleteView(LoginRequiredMixin, DeleteView):
    model = HardwareAsset
    template_name = 'assets/hardware/delete.html'
    success_url = reverse_lazy('assets:hardware_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, '硬體資產已成功刪除！')
        return super().delete(request, *args, **kwargs)

# 軟體授權視圖
class SoftwareLicenseListView(LoginRequiredMixin, ListView):
    model = SoftwareLicense
    template_name = 'assets/software/list.html'
    context_object_name = 'licenses'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = SoftwareLicense.objects.select_related('vendor')
        form = LicenseSearchForm(self.request.GET)
        
        if form.is_valid():
            search = form.cleaned_data.get('search')
            license_type = form.cleaned_data.get('license_type')
            status = form.cleaned_data.get('status')
            expiring_soon = form.cleaned_data.get('expiring_soon')
            
            if search:
                queryset = queryset.filter(
                    Q(software_name__icontains=search) |
                    Q(version__icontains=search)
                )
            
            if license_type:
                queryset = queryset.filter(license_type=license_type)
                
            if status:
                queryset = queryset.filter(status=status)
                
            if expiring_soon:
                thirty_days_later = timezone.now().date() + timedelta(days=30)
                queryset = queryset.filter(
                    expiry_date__lte=thirty_days_later,
                    expiry_date__gte=timezone.now().date()
                )
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = LicenseSearchForm(self.request.GET)
        return context

class SoftwareLicenseDetailView(LoginRequiredMixin, DetailView):
    model = SoftwareLicense
    template_name = 'assets/software/detail.html'
    context_object_name = 'license'

class SoftwareLicenseCreateView(LoginRequiredMixin, CreateView):
    model = SoftwareLicense
    form_class = SoftwareLicenseForm
    template_name = 'assets/software/form.html'
    success_url = reverse_lazy('assets:software_list')
    
    def form_valid(self, form):
        messages.success(self.request, '軟體授權已成功新增！')
        return super().form_valid(form)

class SoftwareLicenseUpdateView(LoginRequiredMixin, UpdateView):
    model = SoftwareLicense
    form_class = SoftwareLicenseForm
    template_name = 'assets/software/form.html'
    
    def get_success_url(self):
        return reverse_lazy('assets:software_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, '軟體授權已成功更新！')
        return super().form_valid(form)

class SoftwareLicenseDeleteView(LoginRequiredMixin, DeleteView):
    model = SoftwareLicense
    template_name = 'assets/software/delete.html'
    success_url = reverse_lazy('assets:software_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, '軟體授權已成功刪除！')
        return super().delete(request, *args, **kwargs)

# 供應商視圖
class VendorListView(LoginRequiredMixin, ListView):
    model = Vendor
    template_name = 'assets/vendor/list.html'
    context_object_name = 'vendors'
    paginate_by = 20

class VendorDetailView(LoginRequiredMixin, DetailView):
    model = Vendor
    template_name = 'assets/vendor/detail.html'
    context_object_name = 'vendor'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 該供應商的硬體資產
        context['hardware_assets'] = self.object.hardwareasset_set.all()[:5]
        # 該供應商的軟體授權
        context['software_licenses'] = self.object.softwarelicense_set.all()[:5]
        return context

class VendorCreateView(LoginRequiredMixin, CreateView):
    model = Vendor
    form_class = VendorForm
    template_name = 'assets/vendor/form.html'
    success_url = reverse_lazy('assets:vendor_list')
    
    def form_valid(self, form):
        messages.success(self.request, '供應商已成功新增！')
        return super().form_valid(form)

class VendorUpdateView(LoginRequiredMixin, UpdateView):
    model = Vendor
    form_class = VendorForm
    template_name = 'assets/vendor/form.html'
    
    def get_success_url(self):
        return reverse_lazy('assets:vendor_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, '供應商資料已成功更新！')
        return super().form_valid(form)

class VendorDeleteView(LoginRequiredMixin, DeleteView):
    model = Vendor
    template_name = 'assets/vendor/delete.html'
    success_url = reverse_lazy('assets:vendor_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, '供應商已成功刪除！')
        return super().delete(request, *args, **kwargs)

# 採購申請視圖
class PurchaseRequestListView(LoginRequiredMixin, ListView):
    model = PurchaseRequest
    template_name = 'assets/purchase/list.html'
    context_object_name = 'requests'
    paginate_by = 20

class PurchaseRequestDetailView(LoginRequiredMixin, DetailView):
    model = PurchaseRequest
    template_name = 'assets/purchase/detail.html'
    context_object_name = 'request'

class PurchaseRequestCreateView(LoginRequiredMixin, CreateView):
    model = PurchaseRequest
    form_class = PurchaseRequestForm
    template_name = 'assets/purchase/form.html'
    success_url = reverse_lazy('assets:purchase_list')
    
    def form_valid(self, form):
        form.instance.requester = self.request.user
        messages.success(self.request, '採購申請已成功提交！')
        return super().form_valid(form)

class PurchaseRequestUpdateView(LoginRequiredMixin, UpdateView):
    model = PurchaseRequest
    form_class = PurchaseRequestForm
    template_name = 'assets/purchase/form.html'
    
    def get_success_url(self):
        return reverse_lazy('assets:purchase_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, '採購申請已成功更新！')
        return super().form_valid(form)

class PurchaseRequestDeleteView(LoginRequiredMixin, DeleteView):
    model = PurchaseRequest
    template_name = 'assets/purchase/delete.html'
    success_url = reverse_lazy('assets:purchase_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, '採購申請已成功刪除！')
        return super().delete(request, *args, **kwargs)

class PurchaseRequestApprovalView(LoginRequiredMixin, UpdateView):
    model = PurchaseRequest
    form_class = PurchaseRequestApprovalForm
    template_name = 'assets/purchase/approve.html'
    
    def get_success_url(self):
        return reverse_lazy('assets:purchase_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        form.instance.approver = self.request.user
        form.instance.approval_date = timezone.now()
        messages.success(self.request, '採購申請審核完成！')
        return super().form_valid(form)

# 維修記錄視圖
class MaintenanceRecordListView(LoginRequiredMixin, ListView):
    model = MaintenanceRecord
    template_name = 'assets/maintenance/list.html'
    context_object_name = 'records'
    paginate_by = 20

class MaintenanceRecordDetailView(LoginRequiredMixin, DetailView):
    model = MaintenanceRecord
    template_name = 'assets/maintenance/detail.html'
    context_object_name = 'record'

class MaintenanceRecordCreateView(LoginRequiredMixin, CreateView):
    model = MaintenanceRecord
    form_class = MaintenanceRecordForm
    template_name = 'assets/maintenance/form.html'
    success_url = reverse_lazy('assets:maintenance_list')
    
    def form_valid(self, form):
        messages.success(self.request, '維修記錄已成功新增！')
        return super().form_valid(form)

class MaintenanceRecordUpdateView(LoginRequiredMixin, UpdateView):
    model = MaintenanceRecord
    form_class = MaintenanceRecordForm
    template_name = 'assets/maintenance/form.html'
    
    def get_success_url(self):
        return reverse_lazy('assets:maintenance_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, '維修記錄已成功更新！')
        return super().form_valid(form)

class MaintenanceRecordDeleteView(LoginRequiredMixin, DeleteView):
    model = MaintenanceRecord
    template_name = 'assets/maintenance/delete.html'
    success_url = reverse_lazy('assets:maintenance_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, '維修記錄已成功刪除！')
        return super().delete(request, *args, **kwargs)

# 資產類別視圖
class AssetCategoryListView(LoginRequiredMixin, ListView):
    model = AssetCategory
    template_name = 'assets/category/list.html'
    context_object_name = 'categories'

class AssetCategoryCreateView(LoginRequiredMixin, CreateView):
    model = AssetCategory
    form_class = AssetCategoryForm
    template_name = 'assets/category/form.html'
    success_url = reverse_lazy('assets:category_list')
    
    def form_valid(self, form):
        messages.success(self.request, '資產類別已成功新增！')
        return super().form_valid(form)

class AssetCategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = AssetCategory
    form_class = AssetCategoryForm
    template_name = 'assets/category/form.html'
    success_url = reverse_lazy('assets:category_list')
    
    def form_valid(self, form):
        messages.success(self.request, '資產類別已成功更新！')
        return super().form_valid(form)

class AssetCategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = AssetCategory
    template_name = 'assets/category/delete.html'
    success_url = reverse_lazy('assets:category_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, '資產類別已成功刪除！')
        return super().delete(request, *args, **kwargs)

# 報表和提醒視圖
class AssetReportsView(LoginRequiredMixin, TemplateView):
    template_name = 'assets/reports.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 資產總值統計
        context['total_asset_value'] = HardwareAsset.objects.aggregate(
            total=Sum('purchase_price')
        )['total'] or 0
        
        # 依類別統計資產數量
        context['category_counts'] = HardwareAsset.objects.values(
            'category'
        ).annotate(count=Count('id')).order_by('-count')
        
        # 依狀態統計資產
        context['status_counts'] = HardwareAsset.objects.values(
            'status'
        ).annotate(count=Count('id'))
        
        # 月度採購趨勢
        from django.db.models import TruncMonth
        context['monthly_purchases'] = HardwareAsset.objects.filter(
            purchase_date__isnull=False
        ).annotate(
            month=TruncMonth('purchase_date')
        ).values('month').annotate(
            count=Count('id'),
            total_cost=Sum('purchase_price')
        ).order_by('month')
        
        return context

class WarrantyAlertsView(LoginRequiredMixin, ListView):
    template_name = 'assets/warranty_alerts.html'
    context_object_name = 'assets'
    
    def get_queryset(self):
        thirty_days_later = timezone.now().date() + timedelta(days=30)
        return HardwareAsset.objects.filter(
            warranty_end_date__lte=thirty_days_later,
            warranty_end_date__gte=timezone.now().date()
        ).order_by('warranty_end_date')

class LicenseAlertsView(LoginRequiredMixin, ListView):
    template_name = 'assets/license_alerts.html'
    context_object_name = 'licenses'
    
    def get_queryset(self):
        thirty_days_later = timezone.now().date() + timedelta(days=30)
        return SoftwareLicense.objects.filter(
            expiry_date__lte=thirty_days_later,
            expiry_date__gte=timezone.now().date()
        ).order_by('expiry_date')

# API視圖
@login_required
def asset_search_api(request):
    """資產搜尋API"""
    query = request.GET.get('q', '')
    assets = HardwareAsset.objects.filter(
        Q(asset_tag__icontains=query) |
        Q(name__icontains=query) |
        Q(brand__icontains=query) |
        Q(model__icontains=query)
    )[:10]
    
    data = [{
        'id': asset.id,
        'text': f"{asset.asset_tag} - {asset.name}",
        'brand': asset.brand,
        'model': asset.model
    } for asset in assets]
    
    return JsonResponse({'results': data})

@login_required
def license_search_api(request):
    """軟體授權搜尋API"""
    query = request.GET.get('q', '')
    licenses = SoftwareLicense.objects.filter(
        Q(software_name__icontains=query) |
        Q(version__icontains=query)
    )[:10]
    
    data = [{
        'id': license.id,
        'text': f"{license.software_name} ({license.version})",
        'available': license.available_licenses
    } for license in licenses]
    
    return JsonResponse({'results': data})
