# Generated by Django 3.0.2 on 2020-01-22 07:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studentg', '0003_auto_20200122_1301'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grievance',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='img/'),
        ),
    ]