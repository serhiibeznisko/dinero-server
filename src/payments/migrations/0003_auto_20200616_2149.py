# Generated by Django 2.2.10 on 2020-06-16 21:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0002_auto_20200616_2144'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exchangerate',
            name='from_currency',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='from_currency_rate_set', to='payments.Currency'),
        ),
        migrations.AlterField(
            model_name='exchangerate',
            name='to_currency',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='to_currency_rate_set', to='payments.Currency'),
        ),
    ]