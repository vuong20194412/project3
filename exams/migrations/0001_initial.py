# Generated by Django 4.2.8 on 2023-12-05 08:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Exam',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='name')),
                ('code', models.CharField(max_length=255, unique=True, verbose_name='code')),
                ('_questions', models.TextField(verbose_name='questions')),
                ('_optional_answers', models.TextField(verbose_name='optional answers')),
                ('_correct_answers', models.TextField(verbose_name='correct answers')),
                ('_user_codes', models.TextField(verbose_name='user codes')),
                ('begin_on', models.DateTimeField(null=True, verbose_name='begin on')),
                ('end_on', models.DateTimeField(null=True, verbose_name='end on')),
                ('created_on', models.DateTimeField(verbose_name='created on')),
                ('time', models.CharField(max_length=15, verbose_name='time')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='created by')),
            ],
        ),
        migrations.CreateModel(
            name='Test',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='name')),
                ('code', models.CharField(max_length=255, unique=True, verbose_name='code')),
                ('_answers', models.TextField(verbose_name='answers')),
                ('score', models.FloatField(verbose_name='score')),
                ('created_on', models.DateTimeField(verbose_name='created on')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='created by')),
                ('exam_id', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='exams.exam', verbose_name='exam')),
            ],
        ),
    ]
