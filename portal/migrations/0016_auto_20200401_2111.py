# Generated by Django 3.0.3 on 2020-04-01 13:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0015_auto_20200319_0103'),
    ]

    operations = [
        migrations.AddField(
            model_name='consumeinfo',
            name='cost',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=16),
        ),
        migrations.AddField(
            model_name='consumeinfo',
            name='print_date',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='consumeinfo',
            name='status',
            field=models.CharField(choices=[('fail', '已提交'), ('pending', '未发货'), ('done', '已发货')], default='pending', max_length=50),
        ),
    ]