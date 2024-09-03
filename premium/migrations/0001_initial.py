# Generated by Django 4.2.2 on 2024-09-03 11:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Premium',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_of_payment', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_used_trial', models.BooleanField(default=True)),
                ('bazhay_user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='premium', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
