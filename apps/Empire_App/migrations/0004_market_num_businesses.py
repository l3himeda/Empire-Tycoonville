# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2019-03-27 23:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Empire_App', '0003_market_started'),
    ]

    operations = [
        migrations.AddField(
            model_name='market',
            name='num_businesses',
            field=models.IntegerField(default=0),
        ),
    ]
