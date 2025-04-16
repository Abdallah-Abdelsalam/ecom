from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from .models import Order, OrderItem




def notify_vendor(order):
    from_email = settings.DEFAULT_FROM_EMAIL

    # Loop through each vendor associated with the order
    for vendor in order.vendors.all():
        # Get only the items for this vendor
        vendor_items = order.items.filter(vendor=vendor)

        # Skip if no items (just in case)
        if not vendor_items.exists():
            continue

        subject = f"New Order from {order.user.first_name if order.user else 'Guest'}"
        to_email = vendor.user.email  # assumes vendor.user is a User object
        text_content = f"You have a new order that includes your products."

        # Render vendor-specific email template with order and vendor context
        html_content = render_to_string('order/email_notify_vendor.html', {
            'order': order,
            'vendor': vendor,
            'vendor_items': vendor_items,
        })

        msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()


def notify_customer(order):
    from_email = settings.DEFAULT_FROM_EMAIL

    to_email = order.email
    subject = f"Your Order #{order.id} has been placed!"
    text_content = f"Thank Your for your order! Your order number is #{order.id}."
    html_content = render_to_string('order/email_notify_customer.html', {'order': order})

    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()

def contact_mail(fullname, email, phone, subject, message):
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = email
    subject = f"Contact Form Submission: {subject}"
    text_content = f"Name: {fullname}\nEmail: {email}\nPhone: {phone}\nMessage: {message}"

    html_content = render_to_string('app/contact_email.html', {
        'fullname': fullname,
        'email': email,
        'phone': phone,
        'subject': subject,
        'message': message
    })

    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()