# Generated by Django 3.0.8 on 2020-08-05 15:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0003_auto_20200802_1134'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='img_url',
            field=models.URLField(blank=True, verbose_name='Image URL'),
        ),
    ]