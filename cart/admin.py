from django.contrib import admin
from .models import Order, Item
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db.models import Sum
from django.template.response import TemplateResponse
from django.urls import path

class OrderAdmin(admin.ModelAdmin):
    change_list_template = 'admin/cart/order/change_list.html'

    def get_urls(self):
        custom_urls = [
            path('top-buyer/', self.admin_site.admin_view(self.top_buyer_view), name='cart_order_top_buyer',
            ),
        ]
        return custom_urls + super().get_urls()

    def top_buyer_view(self, request):
        if not self.has_view_permission(request):
            raise PermissionDenied

        top_buyer = (User.objects.annotate(purchase_count=Sum('order__item__quantity')).filter(purchase_count__gt=0).order_by('-purchase_count', 'username').first())

        context = {
            **self.admin_site.each_context(request),
            'title': 'Top buyer',
            'opts': self.model._meta,
            'top_buyer': top_buyer,
        }

        return TemplateResponse(
            request, 
            'admin/cart/order/top_buyer.html',
            context
        )

admin.site.register(Order, OrderAdmin)
admin.site.register(Item)