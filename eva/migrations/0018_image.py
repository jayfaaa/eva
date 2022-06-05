# Generated by Django 3.2.9 on 2022-03-23 11:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('eva', '0017_questioncategory_percentage'),
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='images')),
                ('reference', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='eva.appuser')),
            ],
        ),
    ]