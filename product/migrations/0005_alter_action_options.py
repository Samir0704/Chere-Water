# Generated by Django 5.1 on 2024-08-28 18:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0004_remove_product_action_product_discount'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='action',
            options={'verbose_name': 'Action', 'verbose_name_plural': 'Action'},
        ),
    ]
