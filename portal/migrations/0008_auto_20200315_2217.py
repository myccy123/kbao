# Generated by Django 3.0.3 on 2020-03-15 14:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0007_userinfo_def_express'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExpressOrderInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_date', models.DateTimeField(auto_now_add=True)),
                ('update_date', models.DateTimeField(auto_now=True)),
                ('valid', models.CharField(blank=True, choices=[('', '未选择'), ('1', '有效'), ('0', '无效')], default='1', max_length=10)),
                ('express_type', models.CharField(blank=True, max_length=50)),
                ('order_id', models.CharField(blank=True, max_length=50)),
                ('order_status', models.CharField(blank=True, default='1', max_length=50)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='consumeinfo',
            name='order_id',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
