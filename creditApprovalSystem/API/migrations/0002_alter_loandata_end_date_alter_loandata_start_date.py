# Generated by Django 5.0.1 on 2024-01-15 19:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('API', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loandata',
            name='end_date',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='loandata',
            name='start_date',
            field=models.CharField(max_length=255),
        ),
    ]
