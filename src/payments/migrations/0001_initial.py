# Generated by Django 2.2.10 on 2020-06-16 21:08

import core.mixins
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
            name='Currency',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Last updated at')),
                ('name', models.CharField(max_length=32, unique=True)),
                ('code', models.CharField(max_length=32, unique=True)),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Wallet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Last updated at')),
                ('balance', models.FloatField(default=0)),
                ('currency', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='wallet_set', to='payments.Currency')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='wallet_set', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'currency')},
            },
            bases=(models.Model, core.mixins.UpdateMixin),
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Last updated at')),
                ('amount', models.FloatField(default=0)),
                ('status', models.CharField(choices=[('PENDING', 'PENDING'), ('SUCCESSFUL', 'SUCCESSFUL'), ('CANCELED', 'CANCELED')], max_length=15)),
                ('paid_at', models.DateTimeField()),
                ('currency', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='transaction_set', to='payments.Currency')),
                ('from_user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='from_transaction_set', to='payments.Wallet')),
                ('to_user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='to_transaction_set', to='payments.Wallet')),
            ],
            options={
                'ordering': ('-id',),
            },
        ),
        migrations.CreateModel(
            name='ExchangeRate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Last updated at')),
                ('amount', models.FloatField(default=0)),
                ('from_currency', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='from_currency_rate_set', to='payments.Wallet')),
                ('to_currency', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='to_currency_rate_set', to='payments.Wallet')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
