from django.contrib import admin
from .models import *


class Product_Images(admin.TabularInline):
    model = Product_Image

class additional_informations(admin.TabularInline):
    model = additional_information


class Product_admin(admin.ModelAdmin):
    inlines = (Product_Images, additional_informations)
    

admin.site.register(Vendor)


admin.site.register(Section)
admin.site.register(Product, Product_admin)
admin.site.register(Product_Image)
admin.site.register(Color)
admin.site.register(Size)
admin.site.register(ProductVariation)



admin.site.register(ProductColor)
admin.site.register(additional_information)
admin.site.register(Brand)

admin.site.register(slider)
admin.site.register(banner_area)

admin.site.register(Main_Category)
admin.site.register(Category)
admin.site.register(Sub_Category)


admin.site.register(Coupon_Code)


admin.site.register(Order)
admin.site.register(OrderItem)
