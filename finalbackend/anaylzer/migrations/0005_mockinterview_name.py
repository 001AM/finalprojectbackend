# Generated by Django 5.0.7 on 2024-10-20 22:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anaylzer', '0004_mockinterview_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='mockinterview',
            name='name',
            field=models.CharField(default='', max_length=20),
        ),
    ]
