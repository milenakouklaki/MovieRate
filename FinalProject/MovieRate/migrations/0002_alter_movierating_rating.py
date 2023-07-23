# Generated by Django 4.2.3 on 2023-07-18 10:55

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MovieRate', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movierating',
            name='rating',
            field=models.PositiveIntegerField(default=0, validators=[django.core.validators.MaxValueValidator(5)]),
        ),
    ]
