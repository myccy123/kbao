# Generated by Django 3.0.3 on 2020-03-15 06:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0004_auto_20200315_1421'),
    ]

    operations = [
        migrations.AddField(
            model_name='consumeinfo',
            name='express_name',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
