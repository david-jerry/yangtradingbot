# Generated by Django 4.2.4 on 2023-09-24 12:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0021_sniper_decimal_sniper_symbol'),
    ]

    operations = [
        migrations.CreateModel(
            name='copytradetxhash',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id_copy', models.CharField(blank=True, max_length=500)),
                ('txhash', models.CharField(blank=True, max_length=500)),
                ('bot_name', models.CharField(blank=True, max_length=500)),
                ('amount', models.CharField(blank=True, max_length=500)),
            ],
        )
    ]
