# Generated by Django 3.2.9 on 2021-12-05 16:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eva', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='evaluationsheet',
            name='comments_and_recommendations',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]