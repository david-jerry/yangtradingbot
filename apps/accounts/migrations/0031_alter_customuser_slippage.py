# Generated by Django 4.2.4 on 2023-09-29 17:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0030_tradetxhash"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customuser",
            name="slippage",
            field=models.DecimalField(decimal_places=2, default=20.0, max_digits=20),
        ),
    ]