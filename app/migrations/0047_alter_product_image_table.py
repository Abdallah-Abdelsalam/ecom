# Generated by Django 5.1.5 on 2025-05-07 19:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0046_remove_order_shipping_zone_delete_shippingzone"),
    ]

    operations = [
        migrations.AlterModelTable(
            name="product_image",
            table="app_Product_Image",
        ),
    ]
