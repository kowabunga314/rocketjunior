# Generated by Django 5.1.5 on 2025-01-26 07:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('entity', '0011_alter_entity_name_alter_entity_path'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attribute',
            name='value',
            field=models.DecimalField(blank=True, decimal_places=10, max_digits=20, null=True),
        ),
    ]
