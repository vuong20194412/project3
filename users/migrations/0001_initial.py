# Generated by Django 4.2.8 on 2023-12-05 08:41

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('name', models.CharField(max_length=255, verbose_name='fullname')),
                ('code', models.CharField(max_length=255, unique=True, verbose_name='code')),
                ('email', models.EmailField(max_length=255, unique=True, verbose_name='email')),
                ('created_on', models.DateTimeField(verbose_name='created on')),
                ('updated_on', models.DateTimeField(verbose_name='updated on')),
                ('is_active', models.BooleanField(default=True)),
                ('is_admin', models.BooleanField(default=False)),
                ('is_staff', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
