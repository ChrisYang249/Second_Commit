# Generated by Django 4.2.3 on 2025-02-11 03:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bis_projects', '0007_alter_sample_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sample',
            name='status',
            field=models.CharField(choices=[('LAB', 'LAB'), ('Sequencing', 'Sequencing'), ('RESEQ', 'RESEQ'), ('Seq_Complete', 'Seq Complete'), ('Ready', 'Ready'), ('FAIL', 'FAIL')], default='LAB', max_length=50),
        ),
    ]
