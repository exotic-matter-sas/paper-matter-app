# Generated by Django 2.2.5 on 2019-10-31 16:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ftldocument',
            name='language',
            field=models.CharField(max_length=64, null=True),
        ),
    ]
