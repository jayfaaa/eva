# Generated by Django 3.2.9 on 2022-01-19 05:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eva', '0011_alter_evaluationsheet_comments_and_recommendations'),
    ]

    operations = [
        migrations.AlterField(
            model_name='evaluationsheet',
            name='evaluator_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
