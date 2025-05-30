# Generated by Django 5.1.5 on 2025-02-04 08:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0019_remove_cart_colors_remove_orderitem_color"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProductColor",
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
                ("stock", models.PositiveIntegerField(default=0)),
                (
                    "color",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="product_colors",
                        to="app.color",
                    ),
                ),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="product_colors",
                        to="app.product",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="cart",
            name="product_color",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="app.productcolor",
            ),
        ),
        migrations.AddField(
            model_name="orderitem",
            name="product_color",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="app.productcolor",
            ),
        ),
    ]
