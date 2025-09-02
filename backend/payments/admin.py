from django.contrib import admin
from django.utils.html import format_html

from .models import SubscriptionPlan, UserSubscription, PaymentHistory


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'plan_type', 'billing_cycle', 'price', 
        'display_price', 'is_active', 'sort_order'
    ]
    list_filter = ['plan_type', 'billing_cycle', 'is_active']
    search_fields = ['name', 'description']
    ordering = ['sort_order', 'name']
    readonly_fields = ['display_price', 'yearly_price', 'monthly_price']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'plan_type', 'billing_cycle', 'price', 'description')
        }),
        ('Stripe Integration', {
            'fields': ('stripe_price_id', 'stripe_product_id'),
            'classes': ('collapse',)
        }),
        ('Features & Settings', {
            'fields': ('features', 'trial_days', 'is_active', 'sort_order')
        }),
        ('Calculated Fields', {
            'fields': ('display_price', 'yearly_price', 'monthly_price'),
            'classes': ('collapse',)
        }),
    )


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = [
        'user_email', 'plan_name', 'status', 'is_active', 
        'current_period_end', 'trial_days_remaining'
    ]
    list_filter = ['status', 'plan__plan_type', 'plan__billing_cycle']
    search_fields = ['user__email', 'user__username', 'plan__name']
    readonly_fields = [
        'is_active', 'is_trial', 'days_until_expiry', 'trial_days_remaining'
    ]
    
    fieldsets = (
        ('User & Plan', {
            'fields': ('user', 'plan')
        }),
        ('Stripe Integration', {
            'fields': ('stripe_subscription_id', 'stripe_customer_id'),
            'classes': ('collapse',)
        }),
        ('Subscription Status', {
            'fields': ('status', 'current_period_start', 'current_period_end')
        }),
        ('Trial Information', {
            'fields': ('trial_start', 'trial_end'),
            'classes': ('collapse',)
        }),
        ('Cancellation', {
            'fields': ('canceled_at', 'cancel_at_period_end'),
            'classes': ('collapse',)
        }),
        ('Calculated Fields', {
            'fields': ('is_active', 'is_trial', 'days_until_expiry', 'trial_days_remaining'),
            'classes': ('collapse',)
        }),
    )
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User Email'
    
    def plan_name(self, obj):
        return f"{obj.plan.name} ({obj.plan.get_billing_cycle_display()})"
    plan_name.short_description = 'Plan'


@admin.register(PaymentHistory)
class PaymentHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'user_email', 'amount', 'currency', 'status', 
        'subscription_plan', 'created'
    ]
    list_filter = ['status', 'currency', 'created']
    search_fields = ['user__email', 'user__username', 'stripe_payment_intent_id']
    readonly_fields = ['created', 'modified']
    ordering = ['-created']
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('user', 'subscription', 'amount', 'currency', 'status')
        }),
        ('Stripe Integration', {
            'fields': ('stripe_payment_intent_id', 'stripe_invoice_id'),
            'classes': ('collapse',)
        }),
        ('Additional Details', {
            'fields': ('description', 'metadata')
        }),
        ('Timestamps', {
            'fields': ('created', 'modified'),
            'classes': ('collapse',)
        }),
    )
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User Email'
    
    def subscription_plan(self, obj):
        return f"{obj.subscription.plan.name} ({obj.subscription.plan.get_billing_cycle_display()})"
    subscription_plan.short_description = 'Subscription Plan'
