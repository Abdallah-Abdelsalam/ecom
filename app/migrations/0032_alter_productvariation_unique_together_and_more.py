# Generated by Django 5.1.5 on 2025-03-12 23:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0031_alter_productvariation_unique_together"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="productvariation",
            unique_together={("product", "size")},
        ),
        migrations.RemoveField(
            model_name="productvariation",
            name="color",
        ),
    ]
