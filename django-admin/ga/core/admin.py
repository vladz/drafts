from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from core.models import Settings, OrderItem, Order, Log


@admin.register(Settings)
class SettingsAdmin(admin.ModelAdmin):
    list_display = ('domain', 'mailing_time', 'mailing_threads',
                    'mails_keeping_days')

    def has_add_permission(self, request):
        return False


class OrderItemsAdmin(admin.TabularInline):
    model = OrderItem
    fields = ('order', 'ttt_id', 'dt_start_sell', 'start_s',
              'end_s', 'status')
    readonly_fields = ('order', 'ttt_id', 'dt_start_sell', 'start_s',
                       'end_s', 'status')

    def has_add_permission(self, request):
        return False


@admin.register(Order)
class OrdersAdmin(admin.ModelAdmin):
    list_display = ('id', 'dt_created', 'dt_dp', 'dp',
                    'd', 'user_email', 'user_name', 'user_id',
                    'status', 'dt_confirmation')
    readonly_fields = ('id', 'dt_created', 'dt_dp', 'dp',
                       'd', 'user_email', 'user_name', 'user_id')
    fields = ('dt_created', 'dt_dp', 'dp', 'd',
              'user_email', 'user_name', 'user_id', 'status')
    inlines = [
        OrderItemsAdmin
    ]

    def has_add_permission(self, request):
        return False


@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = ('order_link', 'dt_created', 'action')
    readonly_fields = ('order_link', 'dt_created', 'action')
    fields = ('order_link', 'dt_created', 'action')

    def has_add_permission(self, request):
        return False

    def order_link(self, obj):
        link = reverse("admin:core_order_change", args=[obj.order.id])
        return format_html(f'<a href="{link}">{obj.order.id}</a>')

    order_link.short_description = _('Заказ')
