# Generated by Django 3.0.3 on 2020-04-08 21:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0021_auto_20200406_2330'),
    ]

    operations = [
        migrations.AlterField(
            model_name='consumeinfo',
            name='receive_addr',
            field=models.CharField(blank=True, max_length=500),
        ),
    ]