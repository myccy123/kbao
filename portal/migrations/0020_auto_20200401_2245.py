# Generated by Django 3.0.3 on 2020-04-01 14:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0019_orgmap_cost'),
    ]

    operations = [
        migrations.CreateModel(
            name='QQServiceInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_date', models.DateTimeField(auto_now_add=True)),
                ('update_date', models.DateTimeField(auto_now=True)),
                ('valid', models.CharField(blank=True, choices=[('', '未选择'), ('1', '有效'), ('0', '无效')], default='1', max_length=10)),
                ('name', models.CharField(blank=True, max_length=50)),
                ('qq', models.CharField(blank=True, max_length=50)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterField(
            model_name='publicnotice',
            name='content',
            field=models.CharField(blank=True, max_length=2000),
        ),
    ]