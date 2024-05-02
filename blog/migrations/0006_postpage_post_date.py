# Generated by Django 4.2.9 on 2024-01-15 18:52

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0005_alter_postpage_body"),
    ]

    operations = [
        migrations.AddField(
            model_name="postpage",
            name="post_date",
            field=models.DateTimeField(
                default=datetime.date.today, verbose_name="post date"
            ),
        ),
    ]
