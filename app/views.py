

from django.http import JsonResponse
from itertools import groupby
from django.utils.text import slugify

from django.conf import settings
from django.core.mail import send_mail

from pyexpat.errors import messages
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.forms import modelformset_factory
from .models import slider,banner_area,Main_Category,Sub_Category,Product,Category,Brand,Coupon_Code,Order, OrderItem,Vendor,Wishlist,Product_Image,ProductVariation,Section
from .models import Cart as Cartt
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from cart.cart import Cart
from django.db.models import Max, Min, Sum
from .forms import ProductForm, ProductImageForm, ProductVariationForm, ContactForm

from .utilities import notify_vendor, notify_customer, contact_mail
from django.db.models import Q



def frontpage(request):
    sliders = slider.objects.all().order_by('-id')[0:3]
    banners = banner_area.objects.all().order_by('-id')[0:3]
    brands = Brand.objects.all()

    main_category = Main_Category.objects.all()
    sub_category = Sub_Category.objects.all()

    categories = Category.objects.all().order_by('-id')[0:3]

    product = Product.objects.filter(section__name = 'Hot Deals')
    newproduct = Product.objects.filter(section__name = 'New arrivals')
    

    context= {
        'sliders': sliders,
        'banners': banners,
        'main_category': main_category,
        'sub_category': sub_category,
        'product':product,
        'brands': brands,
        'categories': categories,
        'newproduct': newproduct,
    }
    return render(request, 'app/frontpage.html', context)  # render the template with the context




def contact(request):
    main_category = Main_Category.objects.all()
    sub_category = Sub_Category.objects.all()
    categories = Category.objects.all()
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Extract cleaned data
            fullname = form.cleaned_data['fullname']
            email = form.cleaned_data['email']
            phone = form.cleaned_data.get('phone', '')  # Use get to avoid KeyError if not provided
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']

            # Compose the email
            contact_mail(fullname, email, phone, subject, message)
            return redirect('contact_thank_you')  # Create a success URL
    else:
        form = ContactForm()

    return render(request, 'app/contact.html', {'form': form, 'main_category': main_category, 'sub_category': sub_category, 'categories': categories})

def contact_thank_you(request):
    # Render a thank you page after successful form submission
    return render(request, 'app/contact_thank_you.html')


def base(request):
    return render(request, 'app/base.html')


def product_detail(request, slug):
    main_category = Main_Category.objects.all()  # Fetch the main categories
    products = Product.objects.all()  # Fetch all products
    categories = Category.objects.all()
    # Fetch product by slug instead of ID
    product = get_object_or_404(Product, slug=slug)

    sub_category = Sub_Category.objects.all()
    # Get related products from the same brand, excluding the current product
    related_products = Product.objects.filter(Brand=product.Brand).exclude(slug=slug)

    # Fetch the product using slug, ensuring no multiple objects
    try:
        product = get_object_or_404(Product, slug=slug)
        variations = product.variations.all()  # Fetch all variations for the product

        # Group variations by size
        variations_by_size = {}
        for variation in variations:
            if variation.size not in variations_by_size:
                variations_by_size[variation.size] = []
            variations_by_size[variation.size].append(variation)

        # Convert dictionary values (grouped variations) into a list
        unique_size_variations = list(variations_by_size.values())

        # Get the base price of the product (if variations exist, the variations can change the price)
        base_price = product.price
        discounted_product_price = base_price - (base_price * product.discount / 100) if product.discount else base_price

        # Prepare discounted prices for each variation
        for variation in variations:
            # Calculate the variation's price with the product discount applied
            variation_price = variation.price
            discounted_variation_price = variation_price - (variation_price * product.discount / 100) if product.discount else variation_price
            variation.discounted_price = discounted_variation_price

        context = {
            'product': product,
            'main_category': main_category,
            'products': products,
            'categories': categories,
            'sub_category': sub_category,
            'unique_size_variations': unique_size_variations,  # Send grouped variations to the template
            'product_price': discounted_product_price,  # Pass the discounted price to the template
            'related_products': related_products,  
        }

        return render(request, 'product/product_detail.html', context)
    
    except Product.DoesNotExist:
        return redirect('404')
 

def Error404(request):
    return render(request, 'errors/404.html')


def My_account(request):
    return render(request, 'account/my_account.html')

def My_account_register(request):
    return render(request, 'account/my_account_register.html')

def Register(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')

        email = request.POST.get('email')
        password = request.POST.get('password')

        # Check if username (email in this case) already exists
        if User.objects.filter(username=email).exists():
            messages.error(request, 'This Email is already taken.')
            return redirect('my_account_register')

        # Check if email already exists (optional, if you want a separate check for the email)
        if User.objects.filter(email=email).exists():
            messages.error(request, 'This Email already exists.')
            return redirect('my_account_register')

        # Proceed with creating the user if no duplicate username/email is found
        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            username=email  # Use email as the username
        )
        user.set_password(password)
        user.save()

        # Redirect to login after successful registration
        messages.success(request, 'Registration successful! Please log in.')
        return redirect('login')

    return render(request, 'registration/register.html')

def Login(request):
    if request.method == "POST":
        username = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request,user)
            return redirect('frontpage')
        else:
            messages.error(request, 'Email or Password is Invalid')
            return redirect('login')



@login_required(login_url='/accounts/login/')
def Profile(request):
    sub_category = Sub_Category.objects.all()
    # Initialize context to include categories and main categories
    categories = Category.objects.all()
    main_category = Main_Category.objects.all()

    try:
        # Try to get the vendor associated with the logged-in user
        vendor = Vendor.objects.get(user=request.user)

        # If user is a vendor, show vendor-specific data
        products = Product.objects.filter(vendor=vendor)
        
        # Fetch the orders for this vendor by joining with order items and filter by the vendor's products
        orders = Order.objects.filter(items__product__vendor=vendor).distinct()

        # Add order items specific to each order (not all orders)
        for order in orders:
            order.order_items = OrderItem.objects.filter(order=order, product__vendor=vendor)

        # Add vendor data to context
        context = {
            'orders': orders,
            'categories': categories,
            'products': products,
            'main_category': main_category,
            'sub_category': sub_category,
        }
        
        return render(request, 'profile/profile.html', context)

    except Vendor.DoesNotExist:
        # If the user is not a vendor, show only their personal orders
        orders = Order.objects.filter(user=request.user)
        for order in orders:
            order.order_items = OrderItem.objects.filter(order=order)

        # Add customer-specific data to context
        context = {
            'orders': orders,
            'categories': categories,
            'main_category': main_category,
        }

        return render(request, 'profile/profile.html', context)

@login_required(login_url='/accounts/login/')
def Profile_Update(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            address = request.POST.get('address')
            email = request.POST.get('email')
            password = request.POST.get('password')
            user_id = request.user.id

            user = User.objects.get(id=user_id)
            user.first_name = first_name
            user.last_name = last_name
            user.address = address
            user.email = email

            if password != None and password != "":
                user.set_password(password)
            user.save()
            messages.success(request, 'Profile has been Successfully updated')

            return redirect('profile')
        


        


def custom_logout(request):
    logout(request)
    return redirect('/') 



def PRODUCT(request):
    category = Main_Category.objects.all()
    product = Product.objects.all()
    main_category = Main_Category.objects.all()
    sub_category = Sub_Category.objects.all()
    brand = Brand.objects.all()
    categories = Category.objects.all()

    products_with_variants = []

    for prod in product:
        variants = prod.variations.all()

        # Group variants by size with an in_stock flag
        size_grouped_variants = {}

        for variant in variants:
            size = variant.size
            if size not in size_grouped_variants:
                size_grouped_variants[size] = {
                    'in_stock': False,
                    'variants': []
                }

            # Mark size as in stock if any variant has stock > 0
            if variant.stock > 0:
                size_grouped_variants[size]['in_stock'] = True

            size_grouped_variants[size]['variants'].append({
                'variant': variant,
                'price': float(variant.price) if isinstance(variant.price, str) else variant.price,
                'stock': variant.stock,
            })

        products_with_variants.append({
            'product': prod,
            'size_grouped_variants': size_grouped_variants,
        })

    context = {
        'category': category,
        'product': products_with_variants,
        'sub_category': sub_category,
        'brand': brand,
        'main_category': main_category,
        'categories': categories,
    }

    return render(request, 'product/product.html', context)


def cart_add(request, id):
    # Get the cart from the request
    cart = Cart(request)
    
    # Get the product, or raise a 404 error if not found
    product = get_object_or_404(Product, id=id)

    # Get the selected size from the form (ensure it's passed via POST request)
    selected_size = request.POST.get('selected_size')  # The size name (e.g., 'S', 'M', 'L')
    selected_quantity = int(request.POST.get('quantity', 1))  # Get quantity from form, default to 1

    # Initialize variation to None and variation_price to base product price
    variation = None
    variation_price = product.price  # Default to the base product price

    # Check if size is selected
    if not selected_size:  # Size is missing
        messages.error(request, "Please select a size.")
        return redirect("product_detail", slug=product.slug)  # Redirect to product details page

    # If size is selected, try to get the variation based on size name
    try:
        if selected_size:
            # Assuming size is represented by name, not id, adjust accordingly.
            variation = ProductVariation.objects.get(
                product=product,
                size__name=selected_size  # Match based on the size name
            )
            variation_price = variation.price  # Update price with variation price
    except ProductVariation.DoesNotExist:
        # If there's no variation, we will proceed to add the base product to the cart
        variation = None
        variation_price = product.price  # Default to base product price

    # Ensure stock is checked, and if not available, return an error
    if variation and variation.stock <= 0:
        messages.error(request, "Selected size variation is out of stock.")
        return redirect("product_detail", slug=product.slug)

    if variation is None and product.availability <= 0:  # In case there's no variation, check the base product stock
        messages.error(request, "The product is out of stock.")
        return redirect("product_detail", slug=product.slug)

    # Add the product (with the selected variation and price) to the cart
    cart.add(product=product, variation=variation, quantity=selected_quantity, price=variation_price, selected_size=selected_size)

    # Redirect to cart details page
    return redirect("cart_detail")

def item_clear(request, product_id, variation_id=None):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)

    # If there's a variation_id, fetch the variation; otherwise, remove the base product
    if variation_id:
        variation = get_object_or_404(ProductVariation, id=variation_id, product=product)
        cart.remove(product, variation)
    else:
        cart.remove(product)

    return redirect("cart_detail")



def item_increment(request, id):
    cart = Cart(request)
    product = Product.objects.get(id=id)
    cart.add(product=product)
    return redirect("cart_detail")



def item_decrement(request, id):
    cart = Cart(request)
    product = Product.objects.get(id=id)
    cart.decrement(product=product)
    return redirect("cart_detail")



def cart_clear(request):
    cart = Cart(request)
    cart.clear()
    return redirect("cart_detail")





def cart_detail(request):
    main_category = Main_Category.objects.all()
    sub_category = Sub_Category.objects.all()
    categories = Category.objects.all()
    
    # Initialize the Cart instance to get the cart data from the session
    cart = Cart(request).cart  # Using the Cart class to access the cart data
    
    # Initialize packing cost and tax
    packing_cost = sum(item.get('packing_cost', 0) for item in cart.values() if item)
    tax = sum(item.get('tax', 0) for item in cart.values() if item)

    # Initialize coupon discount logic
    coupon_discount = 0  # Default to no discount
    coupon_code = None
    if request.method == "GET":
        coupon_code = request.GET.get('coupon_code')
        if coupon_code:
            try:
                coupon = Coupon_Code.objects.get(code=coupon_code)
                coupon_discount = coupon.discount  # Assuming the coupon has a 'discount' field
                messages.success(request, "Coupon applied successfully!")
            except Coupon_Code.DoesNotExist:
                messages.error(request, "Invalid Coupon Code!")

    # Calculate cart total before applying the coupon discount
    cart_total_price = sum(item['price'] * item['quantity'] for item in cart.values() if item)

    # Calculate the discount amount
    discount_amount = cart_total_price * coupon_discount / 100
    total_after_discount = cart_total_price - discount_amount

    # Calculate final total (including tax, shipping, and after applying coupon discount)
    final_total = total_after_discount + tax + 80 # Add shipping if needed

    # Store the discount and final total in session for Checkout
    request.session['coupon_discount'] = coupon_discount
    request.session['final_total'] = final_total
    request.session['cart_total_price'] = cart_total_price
    request.session['tax'] = tax

    # Pass all necessary context data to the template
    context = {
        'cart': cart,
        'cart_total_price': cart_total_price,
        'tax': tax,
        'coupon_discount': coupon_discount,
        'discount_amount': discount_amount,
        'total_after_discount': total_after_discount,
        'final_total': final_total,
        'valid_coupon': coupon_discount > 0,
        'coupon_code': coupon_code,
        'categories': categories,
        'main_category': main_category,
        'sub_category': sub_category,
    }

    return render(request, 'cart/cart.html', context)



def Checkout(request):
    categories = Category.objects.all()
    # Retrieve the stored session values for coupon discount and final total
    coupon_discount = request.session.get('coupon_discount', 0)
    final_total = request.session.get('final_total', 0)
    cart_total_price = request.session.get('cart_total_price', 0)
    tax = request.session.get('tax', 0)

    # Calculate tax and packing cost (for reference, but final total comes from cart_detail)
    packing_cost = sum(i.get('packing_cost', 0) for i in request.session.get('cart', {}).values() if i)
    tax_and_packing = cart_total_price + packing_cost + tax

    # Pass the necessary context to the template
    context = {
        'tax_and_packing': tax_and_packing,
        'coupon_discount': coupon_discount,
        'cart_total_price': cart_total_price,
        'tax': tax,
        'packing_cost': packing_cost,
        'final_total': final_total,  # Final total calculated in cart_detail
        'categories': categories,
    }

    return render(request, 'checkout/checkout.html', context)



def complete(request):
    if request.method == 'POST':
        coupon_discount = request.session.get('coupon_discount', 0)
        cart = request.session.get('cart', {})

        cart_price = sum(i['price'] * i['quantity'] for i in cart.values() if i)
        discount_amount = cart_price * coupon_discount / 100
        total_after_discount = cart_price - discount_amount

        tax_rate = request.session.get('tax', 0)
        packing_cost = 80
        final_total = total_after_discount + tax_rate + packing_cost

        neworder = Order()
        if request.user.is_authenticated:
            neworder.user = request.user
            neworder.email = request.user.email
        else:
            neworder.email = request.POST.get('email')

        neworder.first_name = request.POST.get('first_name')
        neworder.last_name = request.POST.get('last_name')
        neworder.phone = request.POST.get('phone')
        neworder.address = request.POST.get('address')
        neworder.total_price = final_total
        neworder.save()

        involved_vendors = set()

        for item_id, item_data in cart.items():
            try:
                product_id = item_id.split('-')[0]
                product = Product.objects.get(id=int(product_id))
            except (Product.DoesNotExist, ValueError):
                continue

            quantity = item_data['quantity']
            price = item_data['price']
            selected_size = item_data['selected_size']

            item_price_after_discount = price * (1 - coupon_discount / 100)
            item_packing_cost = packing_cost
            total_price = item_price_after_discount + item_packing_cost

            order_item = OrderItem.objects.create(
                order=neworder,
                product=product,
                vendor=product.vendor,  # Assign the vendor here
                price=total_price,
                quantity=quantity,
                size=selected_size
            )

            # Track unique vendors
            involved_vendors.add(product.vendor)

            variation = product.variations.filter(size__name=selected_size).first()
            if variation and variation.stock >= quantity:
                variation.stock -= quantity
                variation.save()

            if product.total_quantity >= quantity:
                product.total_quantity -= quantity
                product.save()

        # Attach all vendors to the order
        neworder.vendors.set(involved_vendors)

        # Clear cart
        request.session['cart'] = {}

        # Notify customer and vendors
        notify_vendor(neworder)  # You may want to send per vendor
        notify_customer(neworder)

        messages.success(request, 'Order has been placed successfully')
        return render(request, 'checkout/success.html', {'order_id': neworder.id})

    return render(request, 'checkout/success.html')


# Vendor Dashboard: List of products
@login_required
def vendor_dashboard(request):
    try:
        vendor = Vendor.objects.get(user=request.user)
        products = Product.objects.filter(vendor=vendor)

        # Fetch orders for this vendor by joining with order items
        orders = Order.objects.filter(items__product__vendor=vendor).distinct()

        # Fetch all order items for the orders related to this vendor
        order_items = OrderItem.objects.filter(product__vendor=vendor)

        # Calculate total sales (number of orders for this vendor)
        total_sales = orders.count()

        # Calculate total revenue (sum of the total price for each order item)
        total_revenue = sum(item.price for item in order_items)

        context = {
            'vendor': vendor,
            'products': products,
            'orders': orders,
            'order_items': order_items,
            'total_sales': total_sales,
            'total_revenue': total_revenue,
        }

        return render(request, 'vendor/dashboard.html', context)

    except Vendor.DoesNotExist:
        return redirect('404')

# Post Product (Add a new product)
@login_required
def post_product(request):
    vendor = Vendor.objects.get(user=request.user)

    if request.method == 'POST':
        form = ProductForm(request.POST or None, request.FILES or None)

        # Create a formset for ProductImageForm and get the images from request.FILES
        image_formset = ProductImageForm((request.POST, request.FILES) or None)

        if form.is_valid() and image_formset.is_valid():
            # Save the product object
            product = form.save(commit=False)
            product.Brand = vendor.brand
            product.packing_cost = 0  # Set the default packing cost
            product.vendor = vendor
            product.tax = 0  # Set the default tax

            # Automatically set the section to "new arrivals"
            new_arrival_section = Section.objects.get(name='New arrivals')  # Make sure you have this section created
            product.section = new_arrival_section  # Set the section to New Arrivals
            
            name_slug = slugify(product.product_name)
            modal_name = name_slug.replace('-', ', ')  # Generate a slug from the model name
            description_slug = slugify(product.description)  # Generate a slug from the description
            product.product_information = description_slug  # Set the product information to the slug
            product.model_name = modal_name  # Set the model name to the slug

            if not product.tags:
                slug = slugify(product.description)  # or form.cleaned_data.get('slug')
                tags = slug.replace('-', ', ')  # or any format you prefer
                product.tags = tags

            product.save()

            # Loop through the images and save each one individually
            for image in request.FILES.getlist('image'):  # Get the list of uploaded images
                product_image = Product_Image(product=product, image=image)
                product_image.save()

            return redirect('vendor_dashboard')
    else:
        form = ProductForm()
        image_formset = ProductImageForm()  # Initialize empty formset for images

    return render(request, 'vendor/post_product.html', {'form': form, 'image_formset': image_formset})

@login_required
def edit_product(request, product_id):
    vendor = Vendor.objects.get(user=request.user)
    product = get_object_or_404(Product, id=product_id, vendor=vendor)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)

        if form.is_valid():
            product = form.save(commit=False)
            product.Brand = vendor.brand
            product.vendor = vendor
            product.packing_cost = product.packing_cost or 0
            product.tax = product.tax or 0

            if not product.section:
                new_arrival_section = Section.objects.get(name='New arrivals')
                product.section = new_arrival_section

            name_slug = slugify(product.product_name)
            modal_name = name_slug.replace('-', ', ')
            description_slug = slugify(product.description)
            product.product_information = description_slug
            product.model_name = modal_name

            if not product.tags:
                tags = slugify(product.description).replace('-', ', ')
                product.tags = tags

            product.save()

            # ✅ Handle multiple images manually
            for image in request.FILES.getlist('image'):
                Product_Image.objects.create(product=product, image=image)

            return redirect('vendor_dashboard')

    else:
        form = ProductForm(instance=product)

    return render(request, 'vendor/post_product.html', {
        'form': form,
        'product': product,
    })


@login_required
def delete_product(request, product_id):
    # Get the product by ID
    product = get_object_or_404(Product, id=product_id)

    # Check if the current user is the vendor who owns the product
    if product.vendor.user != request.user:
        messages.error(request, "You do not have permission to delete this product.")
        return redirect('vendor_dashboard')

    # If the request method is POST, delete the product
    if request.method == 'POST':
        product.delete()
        messages.success(request, "Product has been deleted successfully.")
        return redirect('vendor_dashboard')

    # If the request method is not POST, just display the page (GET)
    return redirect('vendor_dashboard')

@login_required
def post_product_variation(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        if 'variation_id' in request.POST:
            variation = get_object_or_404(ProductVariation, id=request.POST['variation_id'], product=product)
            form = ProductVariationForm(request.POST, instance=variation)
        else:
            form = ProductVariationForm(request.POST)
            form.instance.product = product

        if form.is_valid():
            variation = form.save(commit=False)
            variation.product = product
            variation.save()

            # Update total quantity
            total_stock = product.variations.aggregate(total=Sum('stock'))['total'] or 0
            product.total_quantity = total_stock
            product.save()

            return redirect('post_product_variation', product_id=product.id)

    else:
        if 'variation_id' in request.GET:
            variation = get_object_or_404(ProductVariation, id=request.GET['variation_id'], product=product)
            form = ProductVariationForm(instance=variation)
        else:
            form = ProductVariationForm()

    if request.method == 'POST' and 'delete_product' in request.POST:
        if product.vendor.user != request.user:
            messages.error(request, "You do not have permission to delete this product.")
            return redirect('vendor_dashboard')

        product.delete()
        messages.success(request, "Product has been deleted successfully.")
        return redirect('vendor_dashboard')

    return render(request, 'vendor/post_product_variation.html', {
        'form': form,
        'product': product,
        'variations': product.variations.all(),
    })

@login_required
def edit_product_variation(request, variation_id):
    variation = get_object_or_404(ProductVariation, id=variation_id)
    product = variation.product

    # Ensure the current user owns this product
    if product.vendor.user != request.user:
        messages.error(request, "You do not have permission to edit this variation.")
        return redirect('vendor_dashboard')

    if request.method == 'POST':
        form = ProductVariationForm(request.POST, instance=variation)
        if form.is_valid():
            form.save()

            # Recalculate total quantity
            product.total_quantity = product.variations.aggregate(total=Sum('stock'))['total'] or 0
            product.save()

            messages.success(request, "Variation updated successfully.")
            return redirect('post_product_variation', product_id=product.id)
    else:
        form = ProductVariationForm(instance=variation)

    return render(request, 'vendor/edit_product_variation.html', {
        'form': form,
        'variation': variation,
        'product': product
    })


# View to display the wishlist
@login_required
def wishlist_view(request):
    categories = Category.objects.all()
    # Fetch the user's wishlist
    wishlist_items = Wishlist.objects.filter(user=request.user)
    main_category = Main_Category.objects.all()
    sub_category = Sub_Category.objects.all()

    return render(request, 'wishlist/wishlist.html', {'wishlist_items': wishlist_items, 'main_category': main_category, 'sub_category': sub_category, 'categories': categories})

# View to add a product to the wishlist
@login_required
def add_to_wishlist(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        
        # Check if the product is already in the user's wishlist
        if not Wishlist.objects.filter(user=request.user, product=product).exists():
            Wishlist.objects.create(user=request.user, product=product)
        
        return redirect('wishlist')  # Redirect to the wishlist page

    except Product.DoesNotExist:
        # If the product doesn't exist, handle the error (optional)
        return redirect('wishlist')  # Or return an error page


# View to remove a product from the wishlist
@login_required
def remove_from_wishlist(request, product_id):
    product = Product.objects.get(id=product_id)
    
    # Delete the product from the user's wishlist
    Wishlist.objects.filter(user=request.user, product=product).delete()
    
    return redirect('wishlist')  # Redirect to the wishlist page


def brand_list(request):
    main_category = Main_Category.objects.all()
    sub_category = Sub_Category.objects.all()
    categories = Category.objects.all()
    brands = Brand.objects.all()  # Fetch all brands from the database
    return render(request, 'brands/brand_list.html', {'brands': brands, 'categories': categories, 'main_category': main_category, 'sub_category': sub_category})


def brand_detail(request, brand_id):
    main_category = Main_Category.objects.all()
    sub_category = Sub_Category.objects.all()
    categories = Category.objects.all()
    brand = get_object_or_404(Brand, pk=brand_id)
    products = brand.products.all()  # Access related products using the 'products' related_name
    return render(request, 'brands/brand_detail.html', {'brand': brand, 'products': products, 'categories': categories, 'main_category': main_category, 'sub_category': sub_category})



def category_list(request):
    main_category = Main_Category.objects.all()
    sub_category = Sub_Category.objects.all()
    categories = Category.objects.all()  # Fetch all categories from the database
    return render(request, 'categories/category_list.html', {'categories': categories, 'main_category': main_category, 'sub_category': sub_category})



def category_detail(request, category_id):
    sub_category = Sub_Category.objects.all()
    categories = Category.objects.all()
    category = get_object_or_404(Category, pk=category_id)
    products = category.products.all()  # Access related products using the 'products' related_name
    return render(request, 'categories/category_detail.html', {'category': category, 'products': products, 'categories': categories, 'sub_category': sub_category})



def search(request):
    main_category = Main_Category.objects.all()
    sub_category = Sub_Category.objects.all()
    categories = Category.objects.all()
    query = request.GET.get('q', '')
    product_queryset = Product.objects.all()

    if query:
        product_queryset = product_queryset.filter(
            Q(product_name__icontains=query) |
            Q(featured_image__icontains=query) |
            Q(price__icontains=query) |
            Q(discount__icontains=query)
        )

    # Prepare the same structure expected by your template
    product_data = []
    for product in product_queryset:
        variants = ProductVariation.objects.filter(product=product).select_related('size')
        size_grouped_variants = {}

        for variant in variants:
            size = variant.size
            if size not in size_grouped_variants:
                size_grouped_variants[size] = []
            size_grouped_variants[size].append(variant)

        product_data.append({
            'product': product,
            'size_grouped_variants': size_grouped_variants
        })

    return render(request, 'product/search_results.html', {
        'product': product_data,  # key must match what your template uses: "product"
        'query': query,
        'categories': categories,
        'main_category': main_category,
        'sub_category': sub_category,
    })

@login_required
def mark_order_shipped(request, order_id):
    # Get the order object
    order = get_object_or_404(Order, id=order_id)

    # Check if the current user is the vendor associated with this order
    if request.user.vendor not in order.vendors.all():
        messages.error(request, "You do not have permission to mark this order as shipped.")
        return redirect('vendor_dashboard')

    # Mark the order as shipped
    order.shipped = True
    order.status = "Shipped"  # You can change the status if required
    order.save()

    messages.success(request, "Order has been marked as shipped.")
    return redirect('vendor_dashboard')  # Or wherever you want to redirect