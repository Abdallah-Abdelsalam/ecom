from django.conf import settings
from django.db import models

from django.db.models import Q
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.db.models.signals import pre_save

from PIL import Image
from django.core.files.base import ContentFile
from io import BytesIO


class slider(models.Model):


    DISCOUNT_DEAL= (
        ('HOT DEALS', 'HOT DEALS'),
        ('New Arrivals', 'New Arrivals'),
    )


    brand_name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='media/slider_imgs')
    sale = models.IntegerField()
    Discount_Deal = models.CharField(choices=DISCOUNT_DEAL,max_length=100)
    Discount = models.IntegerField()
    link = models.CharField(max_length=200)


    def __str__(self):
        return self.brand_name
    

class banner_area(models.Model):
    image = models.ImageField(upload_to="media/banner_img")
    Discount_Deal = models.CharField(max_length=100)
    quote = models.CharField(max_length=100)
    Discount = models.IntegerField()
    link = models.CharField(max_length=200,null=True)

    def __str__(self):
        return self.quote
    

class Main_Category(models.Model):
    name = models.CharField(max_length=100)
    #image = models.ImageField(upload_to="media/main_category_img")
    #link = models.CharField(max_length=200)
    
    def __str__(self):
        return self.name
    
class Category(models.Model):
    main_category = models.ForeignKey('Main_Category', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    logo = models.ImageField(upload_to="media/category_img", blank=True, null=True)
    
    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Compress image if logo exists
        if self.logo:
            self.compress_logo()

        super().save(*args, **kwargs)

    def compress_logo(self):
        """
        Compress the logo image by resizing and reducing quality.
        """
        img = Image.open(self.logo)
        
        # Resize the image if it's larger than a certain width (optional)
        max_width = 800
        max_height = 800
        img = self.resize_image(img, max_width, max_height)

        # Save the image with reduced quality to compress it
        output_io_stream = self._compress_image(img)
        
        # Reopen the image from the stream and save it back to the field
        self.logo.save(self.logo.name, output_io_stream, save=False)

    def resize_image(self, img, max_width, max_height):
        """
        Resize the image while maintaining aspect ratio.
        """
        width, height = img.size
        if width > max_width or height > max_height:
            ratio = min(max_width / width, max_height / height)
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)  # Updated here
        return img

    def _compress_image(self, img):
        """
        Compress the image by reducing the quality.
        """
        from io import BytesIO
        img_io = BytesIO()
        img.save(img_io, format='JPEG', quality=75)  # Adjust quality as needed
        img_io.seek(0)
        return img_io
    
class Sub_Category(models.Model):
    category = models.ForeignKey(Category,on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    #image = models.ImageField(upload_to="media/sub_category_img")
    #link = models.CharField(max_length=200)

    def __str__(self):
        return self.category.main_category.name + " -- " + self.category.name + " -- " + self.name
    

class Section(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Color(models.Model):
    name = models.CharField(max_length=100,blank= True,null=True)
    code = models.CharField(max_length=100)

    def __str__(self):
        return self.code
    

class Size(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, blank=True,null=True)

    def __str__(self):
        return self.name




class Brand(models.Model):
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to="media/brand_img",null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True,blank=True,null=True)

    def __str__(self):
        return self.name


class Coupon_Code(models.Model):
    code = models.CharField(max_length=100)
    discount = models.FloatField()

    def __str__(self):
        return self.code



class Vendor(models.Model):
    """Vendor model with one-to-one relation to a Brand."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Link vendor to a user account
    name = models.CharField(max_length=255)  # Vendor name
    description = models.TextField()  # Vendor description
    phone_number = models.CharField(max_length=23)  # Vendor phone number
    date_added = models.DateTimeField(auto_now_add=True)  # Timestamp for when the vendor was added
    brand = models.OneToOneField(Brand, on_delete=models.CASCADE, related_name='vendor', null=True,blank=True)  # One-to-one relationship with Brand

    def __str__(self):
        return self.name 


class Product(models.Model):
    VARIANTS = (
        ('None', 'None'),
        ('Size', 'Size'),
    )
    total_quantity = models.IntegerField()
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='products', null=True, blank=True)  # Link product to a vendor
    availability = models.IntegerField(null=True)
    featured_image = models.ImageField(upload_to='media/product_imgs', max_length=255, blank=True, null=True)
    product_name = models.CharField(max_length=100)
    Brand = models.ForeignKey(Brand, related_name='products', on_delete=models.CASCADE, null=True)
    price = models.IntegerField()
    discount = models.IntegerField()
    tax = models.IntegerField(null=True)
    variant = models.CharField(max_length=10, choices=VARIANTS, default='None')
    packing_cost = models.IntegerField(null=True)
    product_information = models.CharField(max_length=500, null=True)
    model_name = models.CharField(max_length=100)
    categories = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    color = models.ManyToManyField(Color, related_name='products', null=True)
    tags = models.CharField(max_length=100)
    description = models.CharField(max_length=500, null=True)
    section = models.ForeignKey(Section, on_delete=models.DO_NOTHING)
    slug = models.SlugField(default='', max_length=500, null=True, blank=True)
    main_categorys = models.ForeignKey(Main_Category, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.product_name

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse("product_detail", kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        # Compress the featured image if it exists
        if self.featured_image:
            self.compress_featured_image()

        super().save(*args, **kwargs)

    def compress_featured_image(self):
        # Open image and convert to RGB
        image = Image.open(self.featured_image)
        image = image.convert('RGB')

        # Compress and save to memory
        buffer = BytesIO()
        image.save(buffer, format='WEBP', quality=70)
        buffer.seek(0)

        # Set new image to the image field with a clean name
        file_name = self.featured_image.name.rsplit('.', 1)[0] + '.webp'
        self.featured_image.save(file_name, ContentFile(buffer.read()), save=False)

    def resize_image(self, img, max_width, max_height):
        """
        Resize the image while maintaining aspect ratio.
        """
        width, height = img.size
        if width > max_width or height > max_height:
            ratio = min(max_width / width, max_height / height)
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)  # Updated for Pillow 10+
        return img

    def _compress_image(self, img):
        """
        Compress the image by reducing the quality.
        """
        img_io = BytesIO()
        img.save(img_io, format='JPEG', quality=75)  # Adjust quality as needed
        img_io.seek(0)
        return img_io

    class Meta:
        db_table = "app_Product"

def create_slug(instance, new_slug=None):
    slug = slugify(instance.product_name)
    if new_slug is not None:
        slug = new_slug
    qs = Product.objects.filter(slug=slug).order_by("-id")
    exists = qs.exists()
    if exists:
        new_slug = "%s-%s" % (slug, qs.first().id)
        return create_slug(instance, new_slug=new_slug)
    return slug
    

def pre_save_post_receiver(sender, instance, *args,**kwargs):
    if not instance.slug:
        instance.slug = create_slug(instance)

pre_save.connect(pre_save_post_receiver, Product)


    
class Product_Image(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    image = models.ImageField(upload_to='media/product_imgs')


from django.db import models

class ProductVariation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variations')
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    stock = models.PositiveIntegerField(default=0)  # Track available stock for each size
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Price for specific variations
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0, blank=True, null=True)  # Discount for specific variations
    
    class Meta:
        unique_together = ('product', 'size')  # Ensure unique combinations of product and size

    def __str__(self):
        return f"{self.product.product_name} - {self.size.name} - EGP {self.price}"

    def get_discounted_price(self):
        """Return the price after applying the discount (if any)."""
        if self.discount:
            return self.price * (1 - (self.discount / 100))  # Apply the discount percentage
        return self.price

class additional_information(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    specifications = models.CharField(max_length=100)
    details = models.TextField()


class Cart(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    product_qty = models.IntegerField(null=True, blank=True)
    craeted_at = models.DateTimeField(auto_now_add=True)


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['user', 'product']  # Ensure a product is not added twice

    def __str__(self):
        return f'{self.user.username} - {self.product.product_name}'
    
class Order(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    address = models.CharField(max_length=250, null=True, blank=True)
    email = models.EmailField(max_length=300, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    total_price = models.FloatField(null=True, blank=True)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    message = models.TextField(null=True, blank=True)
    vendors = models.ManyToManyField(Vendor, related_name='orders', null=True,blank=True)



    
class OrderItem(models.Model):
    """Order item model"""
    order = models.ForeignKey(Order, related_name='items',on_delete=models.CASCADE, blank=True,null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True, null=True)
    vendor = models.ForeignKey(Vendor, related_name='items', on_delete=models.CASCADE, null=True,blank=True)
    #vendor_paid = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1, null=True, blank=True)

    size = models.CharField(max_length=100, null=True, blank=True)  # You can replace 'size' with any other variation type like color.

    def __str__(self):
        return f"OrderItem {self.id} - {self.product} x {self.quantity}, Size: {self.size if self.size else 'N/A'}"



class ProductColor (models.Model):
    product = models.ForeignKey(Product, related_name='product_colors', on_delete=models.CASCADE)
    color = models.ForeignKey(Color, related_name='product_colors', on_delete=models.CASCADE)
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.product.product_name} - {self.color.name}"