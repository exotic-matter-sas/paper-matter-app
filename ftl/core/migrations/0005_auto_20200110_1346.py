#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.

# Generated by Django 2.2.9 on 2020-01-10 12:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_ftldocument_deleted'),
    ]

    operations = [
        migrations.AddField(
            model_name='ftldocument',
            name='md5',
            field=models.CharField(max_length=32, null=True),
        ),
        migrations.AddField(
            model_name='ftldocument',
            name='size',
            field=models.BigIntegerField(default=0),
        ),
    ]
