# Generated by Django 3.1.4 on 2021-05-05 15:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wardrobe', '0012_auto_20210504_1048'),
    ]

    operations = [
        migrations.AlterField(
            model_name='outfit',
            name='name',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
    ]
