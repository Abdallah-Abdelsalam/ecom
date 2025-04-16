# Generated by Django 5.1.5 on 2025-02-04 12:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0021_remove_cart_product_color_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Size",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=50)),
                ("slug", models.SlugField(unique=True)),
            ],
        ),
        migrations.AddField(
            model_name="product",
            name="sizes",
            field=models.ManyToManyField(related_name="products", to="app.size"),
        ),
    ]
