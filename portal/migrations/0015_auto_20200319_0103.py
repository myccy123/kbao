# Generated by Django 3.0.3 on 2020-03-18 17:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0014_userinfo_role'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chargeinfo',
            name='status',
            field=models.CharField(choices=[('pending', '待审核'), ('done', '已到账'), ('reject', '已拒绝')], default='pending', max_length=50),
        ),
    ]
