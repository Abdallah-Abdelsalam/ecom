# Generated by Django 5.1.5 on 2025-02-02 11:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0015_alter_product_categories"),
    ]

    operations = [
        migrations.AddField(
            model_name="category",
            name="logo",
            field=models.ImageField(
                blank=True, null=True, upload_to="media/category_img"
            ),
        ),
    ]
