# Generated by Django 3.1.2 on 2020-10-31 19:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('game_tracker', '0004_auto_20201031_1903'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='city',
            name='region',
        ),
        migrations.AlterField(
            model_name='city',
            name='region_link',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cities', to='game_tracker.region'),
        ),
    ]
