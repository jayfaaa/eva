# Generated by Django 4.0.5 on 2022-06-04 07:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('eva', '0023_evaluationsheet_evaluate_group'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='question',
            name='category',
        ),
    ]