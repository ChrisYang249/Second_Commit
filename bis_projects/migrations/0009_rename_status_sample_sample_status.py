# Generated by Django 4.2.3 on 2025-02-11 07:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bis_projects', '0008_alter_sample_status'),
    ]

    operations = [
        migrations.RenameField(
            model_name='sample',
            old_name='status',
            new_name='sample_status',
        ),
    ]
