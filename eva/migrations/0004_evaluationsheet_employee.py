# Generated by Django 3.2.9 on 2021-12-12 15:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('eva', '0003_appuser'),
    ]

    operations = [
        migrations.AddField(
            model_name='evaluationsheet',
            name='employee',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='eva.appuser'),
        ),
    ]