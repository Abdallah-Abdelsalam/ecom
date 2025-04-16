# forms.py

from django import forms
from django.forms import modelformset_factory
from .models import Product,Product_Image, ProductVariation, Color, Size
from django.forms.widgets import ClearableFileInput

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['featured_image', 'product_name','total_quantity' ,'main_categorys', 'price', 'discount', 'categories', 'description', 'main_categorys']



# Custom widget to handle multiple file uploads
class MultipleFileInput(ClearableFileInput):
    allow_multiple_selected = True


# Custom form for product images
class ProductImageForm(forms.ModelForm):
    image = forms.FileField(widget=MultipleFileInput(attrs={'multiple': True}), required=False)

    class Meta:
        model = Product_Image
        fields = ['image']


class ProductVariationForm(forms.ModelForm):
    class Meta:
        model = ProductVariation
        fields = ['size', 'price', 'stock', 'discount']


class ContactForm(forms.Form):
    fullname = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=20, required=False)
    subject = forms.CharField(max_length=150, required=True)
    message = forms.CharField(widget=forms.Textarea, required=True)