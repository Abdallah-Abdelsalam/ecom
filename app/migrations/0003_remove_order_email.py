# Generated by Django 5.1.5 on 2025-01-21 13:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0002_order_orderitem"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="order",
            name="email",
        ),
    ]
