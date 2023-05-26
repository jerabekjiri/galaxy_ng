# Generated by Django 3.2.18 on 2023-05-15 14:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('galaxy', '0038_namespace_sync'),
    ]

    operations = [
        migrations.CreateModel(
            name='LegacyRoleDownloadCount',
            fields=[
                ('legacyrole', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='galaxy.legacyrole')),
                ('count', models.IntegerField(default=0)),
            ],
        ),
    ]
