# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-07-20 09:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_auto_20160720_0900'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pos',
            name='datetime',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='seasonaltrend',
            name='datetime',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
