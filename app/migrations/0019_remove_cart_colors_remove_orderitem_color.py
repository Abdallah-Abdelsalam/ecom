# Generated by Django 5.1.5 on 2025-02-04 07:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0018_cart_colors_orderitem_color"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="cart",
            name="colors",
        ),
        migrations.RemoveField(
            model_name="orderitem",
            name="color",
        ),
    ]
