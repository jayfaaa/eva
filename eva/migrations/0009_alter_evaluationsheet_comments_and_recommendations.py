# Generated by Django 3.2.9 on 2022-01-19 02:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eva', '0008_appsettings'),
    ]

    operations = [
        migrations.AlterField(
            model_name='evaluationsheet',
            name='comments_and_recommendations',
            field=models.TextField(null=True),
        ),
    ]
