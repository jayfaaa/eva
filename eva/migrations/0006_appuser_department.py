# Generated by Django 3.2.9 on 2021-12-25 15:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('eva', '0005_department'),
    ]

    operations = [
        migrations.AddField(
            model_name='appuser',
            name='department',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='eva.department'),
        ),
    ]
