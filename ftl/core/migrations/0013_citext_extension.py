from django.db import migrations
from django.contrib.postgres.operations import CITextExtension


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_auto_20190717_1257'),
    ]

    operations = [
        CITextExtension(),
    ]
