# Generated by Django 5.1.5 on 2025-02-04 13:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0022_size_product_sizes"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="product",
            name="sizes",
        ),
    ]
