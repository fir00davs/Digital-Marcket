from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import *
from .forms import CategoryForm

# Register your models here.
# admin.site.register(Category)
# admin.site.register(Product)
# admin.site.register(ModelProduct)
admin.site.register(Characteristic)
admin.site.register(Customer)
admin.site.register(FavoriteProduct)

admin.site.register(Cart)
admin.site.register(ProductCart)

admin.site.register(Delivery)

admin.site.register(Order)
admin.site.register(ProductOrder)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'category_icon')
    list_display_links = ('pk', 'title')
    prepopulated_fields = {'slug': ('title',)}
    form = CategoryForm

    def category_icon(self, obj):
        if obj.icon:
            try:
                return mark_safe(f'<img src="{obj.icon.url}" width="30" >')
            except:
                return 'No icon'
        return 'No icon'


@admin.register(ModelProduct)
class ModelProductAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title')
    list_display_links = ('pk', 'title')
    prepopulated_fields = {'slug': ('title',)}


class ProductCharacteristicInline(admin.TabularInline):
    model = ProductCharacteristic
    fk_name = 'product'
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'price', 'quantity', 'discount', 'category', 'model', 'product_image')
    list_display_links = ('pk', 'title')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ProductCharacteristicInline]
    list_editable = ('price', 'quantity', 'discount')
    list_filter = ('price', 'category', 'model')

    def product_image(self, obj):
        if obj.image:
            try:
                return mark_safe(f'<img src="{obj.image.url}" width="60" >')
            except:
                return 'No image'
        return 'No image'
