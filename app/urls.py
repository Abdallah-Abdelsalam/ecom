from django.urls import include, path
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from . import views
from django.contrib.auth.views import LogoutView




urlpatterns = [
    #error pages
    path('404', views.Error404, name='404'),



    path('', views.frontpage, name='frontpage'),
    path('contact/', views.contact, name='contact'),
    path('contact/thank-you/', views.contact_thank_you, name='contact_thank_you'),
    path('product/<slug:slug>', views.product_detail, name='product_detail'),
    path('product', views.PRODUCT, name='product'),

    # account urls
    path('account/my_account', views.My_account, name='my_account'),
    path('account/my_account_register', views.My_account_register, name='my_account_register'),
    path('account/register', views.Register, name='handleregister'),
    path('account/login', views.Login, name='handlelogin'),
    path('account/profile', views.Profile, name='profile'),
    path('account/profile/update', views.Profile_Update, name="profile_update"),
    path('logout/', LogoutView.as_view(), name='logout'),

    path('accounts/', include('django.contrib.auth.urls')),


    path('cart/add/<int:id>/', views.cart_add, name='cart_add'),
    path('cart/item_clear/<int:product_id>/', views.item_clear, name='item_clear'),
    path('cart/item_clear/<int:product_id>/<int:variation_id>/', views.item_clear, name='item_clear'),
    path('cart/item_increment/<int:id>/',views.item_increment, name='item_increment'),
    path('cart/item_decrement/<int:id>/',views.item_decrement, name='item_decrement'),
    path('cart/cart_clear/', views.cart_clear, name='cart_clear'),
    path('cart/cart-detail/',views.cart_detail,name='cart_detail'),
    path('checkout', views.Checkout,name="checkout"),

    path('complete/', views.complete,name="complete"),
    path('dashboard/', views.vendor_dashboard, name='vendor_dashboard'),
    path('post-product/', views.post_product, name='post_product'),

    path('product/edit/<int:product_id>/', views.edit_product, name='edit_product'),

    path('post-product-variation/<int:product_id>/', views.post_product_variation, name='post_product_variation'),
    path('product/<int:product_id>/delete/', views.delete_product, name='delete_product'),
    path('variation/edit/<int:variation_id>/', views.edit_product_variation, name='edit_product_variation'),
    path('mark-order-shipped/<int:order_id>/', views.mark_order_shipped, name='mark_order_shipped'),


    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),


    path('brands/', views.brand_list, name='brand_list'),
    path('brands/<int:brand_id>/', views.brand_detail, name='brand_detail'),

    path('categories/', views.category_list, name='category_list'),
    path('categories/<int:category_id>/', views.category_detail, name='category_detail'),

    path('search/', views.search, name='search'),


] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
