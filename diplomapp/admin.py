from django.contrib import admin

# Register your models here.
from django.db import models
from .models import User, Shop,Product,Category,Order,OrderItem
from django import forms
@admin.register(Shop)
class AdminShop(admin.ModelAdmin):
    list_display = ('id','name','owner','phone','address')
    list_filter = ('name',)
    search_fields = ('name','owner','address')
    prepopulated_fields = {'slug':('name',)}
    date_hierarchy = 'created'
    ordering = ('id','created')

@admin.register(Category)
class AdminCategory(admin.ModelAdmin):
    list_display = ('id','name','parent','slug',)
    prepopulated_fields = {'slug':('name',)}

@admin.register(Product)
class AdminProduct(admin.ModelAdmin):
    formfield_overrides = {
        models.ManyToManyField: {'widget': forms.CheckboxSelectMultiple},
        #models.ImageField:{ 'widget':forms.FileInput()}
    }
    list_display = ('id', 'shop', 'product_name', 'short_description', 'price')
    list_filter = ('shop', 'product_name')
    search_fields = ('shop', 'product_name', 'short_description')
    prepopulated_fields = {'slug': ('product_name',)}


class OrderItemInline(admin.TabularInline):
    model=OrderItem
    raw_id_fields = ['product',]

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id','status','first_name','last_name','email','city','address','created','updated')
    list_filter = ('created','updated','status')
    inlines = [OrderItemInline]


# ##########################
# from .models import TestProduct,TestImage
# @admin.register(TestProduct)
# class AdminTestProduct(admin.ModelAdmin):
#     formfield_overrides = {
#         #models.ManyToManyField: {'widget': forms.CheckboxSelectMultiple},
#         #models.ImageField: {'widget': forms.FileInput()}
#         models.ImageField:{'widget':forms.FileInput(attrs={'multiple': True})}
#
#     }
# @admin.register(TestImage)
# class AdminTestImage(admin.ModelAdmin):
#     formfield_overrides = {
#         models.ImageField: {'widget': forms.FileInput(attrs={'multiple': True})}
#     }