# Generated by Django 5.1.4 on 2025-01-05 18:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lms_core', '0004_remove_coursecontent_video_url_comment_is_approved_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='max_students',
            field=models.IntegerField(default=30, verbose_name='Maksimal Siswa'),
        ),
    ]
