# Generated by Django 3.1.5 on 2021-10-03 11:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='question',
            old_name='question_txt',
            new_name='question_text',
        ),
    ]
