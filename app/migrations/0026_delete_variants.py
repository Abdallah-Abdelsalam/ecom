# Generated by Django 5.1.5 on 2025-02-05 12:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0025_size_product_variant_variants"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Variants",
        ),
    ]
