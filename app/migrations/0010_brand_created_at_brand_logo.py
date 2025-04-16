# Generated by Django 5.1.5 on 2025-01-29 08:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0009_alter_wishlist_unique_together_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="brand",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name="brand",
            name="logo",
            field=models.ImageField(blank=True, null=True, upload_to="media/brand_img"),
        ),
    ]
