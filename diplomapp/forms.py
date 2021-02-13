from django import forms
from django.contrib.auth.models import User
from .models import Shop,Product,Category,ProductImages,Order,OrderItem

from django.db import models


class UserForm(forms.ModelForm):
    username=forms.CharField(max_length=100,required=True)
    password=forms.CharField(max_length=40,widget=forms.PasswordInput())
    class Meta:
        model=User
        fields=('username','password','first_name','last_name','email')

class UserFormEdit(forms.ModelForm):
    class Meta:
        model=User
        fields=('first_name','last_name')
class ShopForm(forms.ModelForm):
    class Meta:
        model=Shop
        fields=('name','phone','address','logo')




class ProductForm(forms.ModelForm):
    class Meta:
        model=Product
        #fields=('product_name','short_description','description','price','image')
        exclude=('shop','created','slug')
        formfield_overrides = {
            models.ManyToManyField: {'widget': forms.CheckboxSelectMultiple},
        }
        try:
            widgets = {
                'category': forms.CheckboxSelectMultiple(choices=Category.objects.all()),
            }
        except:
            pass

class ImagesForm(forms.ModelForm):
    class Meta:
        model=ProductImages
        fields=('product_image',)
        formfield_overrides = {
            models.ImageField: {'widget': forms.FileInput(attrs={'multiple': True})}
        }
        widgets = {
            'product_image':forms.FileInput(attrs={'multiple':'multiple'}),
        }

class SearchForm(forms.Form):
    query=forms.CharField()

    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)
        self.fields['query'].widget = forms.TextInput(attrs={
            #'id': 'myCustomId',
            'class': 'form-control search-input',
            # 'name': 'myCustomName',
            #'placeholder': 'myCustomPlaceholder'
        })

PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 21)]
class CartAddProductForm(forms.Form):
    quantity = forms.TypedChoiceField(choices=PRODUCT_QUANTITY_CHOICES, coerce=int,label='Количество')
    update = forms.BooleanField(required=False,
                                initial=False,
                                widget=forms.HiddenInput)
    #
    def __init__(self, *args, **kwargs):
        super(CartAddProductForm, self).__init__(*args, **kwargs)
        self.fields['quantity'].widget = forms.Select(choices=PRODUCT_QUANTITY_CHOICES,attrs={
            'class':'form-control',
            'style':'width:200px;margin:auto;'

        })


class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name','phone', 'email', 'city', 'address']




