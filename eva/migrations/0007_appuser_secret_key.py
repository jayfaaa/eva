# Generated by Django 3.2.9 on 2022-01-05 11:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eva', '0006_appuser_department'),
    ]

    operations = [
        migrations.AddField(
            model_name='appuser',
            name='secret_key',
            field=models.CharField(max_length=255, null=True),
        ),
    ]