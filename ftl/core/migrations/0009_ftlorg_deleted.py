#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the Business Source License. See LICENSE at project root for more information.

# Generated by Django 2.2.11 on 2020-04-15 12:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0008_ftldocument_type"),
    ]

    operations = [
        migrations.AddField(
            model_name="ftlorg",
            name="deleted",
            field=models.BooleanField(default=False),
        ),
    ]
