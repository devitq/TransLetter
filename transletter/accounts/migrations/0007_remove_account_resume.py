# Generated by Django 5.0 on 2023-12-19 19:09

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        (
            "accounts",
            "0006_alter_account_balance_alter_account_balance_currency",
        ),
    ]

    operations = [
        migrations.RemoveField(
            model_name="account",
            name="resume",
        ),
    ]
