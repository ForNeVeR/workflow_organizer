# Generated by Django 4.2.7 on 2023-11-12 09:00

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("assignment_handler", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="project",
            name="progress",
        ),
    ]
