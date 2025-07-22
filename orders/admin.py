from django.contrib import admin
from .models import Category, Pizza, Sub, Pasta, Salad, Rice, UserOrder, SavedCarts, Biryani, Rolls, Ni
from tinymce.widgets import TinyMCE
from django.db import models
from django.utils.html import format_html

class CategoryAdmin(admin.ModelAdmin):
    formfield_overrides = {
            models.TextField: {'widget': TinyMCE()},
            }


class UserOrderAdmin(admin.ModelAdmin):
    list_display = ('username', 'status_badge', 'delivered_status', 'delivery_address_short', 'time_of_order')
    list_filter = ('status', 'delivered')
    search_fields = ('username', 'delivery_address')
    list_per_page = 20
    date_hierarchy = 'time_of_order'
    ordering = ('-time_of_order',)
    
    def status_badge(self, obj):
        colors = {
            'received': 'orange',
            'preparing': 'blue',
            'baking': 'darkorange',
            'on_way': 'green',
            'delivered': 'darkgreen'
        }
        return format_html(
            '<span style="color: white; background-color: {}; padding: 3px 8px; border-radius: 10px;">{}</span>',
            colors.get(obj.status, 'gray'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def delivered_status(self, obj):
        return format_html(
            '✅' if obj.delivered else '❌'
        )
    delivered_status.short_description = 'Delivered'
    
    def delivery_address_short(self, obj):
        if obj.delivery_address and len(obj.delivery_address) > 30:
            return f"{obj.delivery_address[:30]}..."
        return obj.delivery_address
    delivery_address_short.short_description = 'Address'

# Register all models
admin.site.register(Category, CategoryAdmin)
admin.site.register(Pizza)
admin.site.register(Sub)
admin.site.register(Pasta)
admin.site.register(Salad)
admin.site.register(UserOrder, UserOrderAdmin) 
admin.site.register(SavedCarts)
admin.site.register(Biryani)
admin.site.register(Rolls)
admin.site.register(Ni)
admin.site.register(Rice)