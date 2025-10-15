# mpgepmc_core/admin.py
from django.contrib import admin
from .models import MpgService, MpgBlog, ServiceRequest, ServicePackage, ServiceFeature, Donation, BankAccount, Project

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """
    Admin view configuration for the Project model.
    """
    list_display = ('title', 'slug', 'category', 'is_published', 'posted_date')
    list_filter = ('is_published', 'category', 'posted_date')
    search_fields = ('title', 'short_description', 'full_description')
    prepopulated_fields = {'slug': ('title',)} # Auto-fills slug from title in real-time
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'category', 'short_description', 'full_description', 'image', 'is_published')
        }),
        ('Dates', {
            'fields': ('posted_date', 'updated_date'),
            'classes': ('collapse',), # Makes this section collapsible
        }),
    )
    readonly_fields = ('posted_date', 'updated_date')


class ServiceFeatureInline(admin.TabularInline):
    model = ServiceFeature
    extra = 1
    fields = ('feature_text', 'is_included', 'order')


class ServicePackageInline(admin.StackedInline):
    model = ServicePackage
    extra = 1
    fields = ('name', 'slug', 'description', 'price', 'duration', 'is_active', 'order') # ADDED 'slug'
    prepopulated_fields = {'slug': ('name',)} # Auto-populate slug from name
    inlines = [ServiceFeatureInline]

@admin.register(MpgService)
class MpgServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'has_packages_for_purchase', 'image', 'created_at', 'updated_at') # Added 'slug'
    list_filter = ('is_active', 'has_packages_for_purchase')
    search_fields = ('name', 'short_description')
    ordering = ('name',)
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'short_description', 'full_description', 'image', 'is_active', 'has_packages_for_purchase') # Added 'slug'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    prepopulated_fields = {'slug': ('name',)} # Auto-populate slug from name
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ServicePackageInline]


@admin.register(MpgBlog)
class MpgBlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'posted_date', 'is_published', 'updated_date')
    list_filter = ('is_published', 'posted_date')
    search_fields = ('title', 'short_summary', 'content')
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'short_summary', 'content', 'feature_image', 'is_published')
        }),
        ('Dates', {
            'fields': ('posted_date', 'updated_date'),
            'classes': ('collapse',),
        }),
    )
    readonly_fields = ('posted_date', 'updated_date')


@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ('mpgservice', 'user_full_name', 'user_email', 'phone_number', 'request_date', 'is_processed')
    list_filter = ('is_processed', 'mpgservice')
    search_fields = ('user_full_name', 'user_email', 'mpgservice__name', 'user_message')
    readonly_fields = ('mpgservice', 'user_full_name', 'user_email', 'phone_number', 'user_message', 'request_date')
    actions = ['mark_as_processed']

    def mark_as_processed(self, request, queryset):
        queryset.update(is_processed=True)
    mark_as_processed.short_description = "Mark selected requests as processed"


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ('donation_order_number', 'amount', 'status', 'full_name', 'email', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('donation_order_number', 'full_name', 'email', 'transaction_id')
    readonly_fields = ('created_at', 'updated_at', 'donation_order_number')
    
    fieldsets = (
        ('Donation Summary', {
            'fields': ('donation_order_number', 'amount', 'status')
        }),
        ('Donor Verification Details', {
            'fields': ('full_name', 'email', 'transaction_id', 'sender_account_name', 'sender_account_number', 'transaction_slip')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_completed', 'mark_as_failed']

    def mark_as_completed(self, request, queryset):
        queryset.update(status=Donation.DonationStatus.COMPLETED)
    mark_as_completed.short_description = "Mark selected donations as Completed"

    def mark_as_failed(self, request, queryset):
        queryset.update(status=Donation.DonationStatus.FAILED)
    mark_as_failed.short_description = "Mark selected donations as Failed"


@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ('account_title', 'bank_name', 'account_number', 'is_active')
    list_filter = ('is_active',)
    actions = ['activate_account']

    def activate_account(self, request, queryset):
        if queryset.count() == 1:
            BankAccount.objects.update(is_active=False)
            queryset.update(is_active=True)
            self.message_user(request, "The selected account has been activated for donations.")
        else:
            self.message_user(request, "Please select only one account to activate.", level='error')
    activate_account.short_description = "Set as the active donation account"


