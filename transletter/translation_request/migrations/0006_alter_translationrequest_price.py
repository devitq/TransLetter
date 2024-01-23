# Generated by Django 5.0.1 on 2024-01-23 14:15

import djmoney.models.fields
import djmoney.models.validators
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        (
            "translation_request",
            "0001_initial_squashed_0005_alter_translationrequest_created_at_and_more",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="translationrequest",
            name="price",
            field=djmoney.models.fields.MoneyField(
                currency_choices=(("USD", "Dollar"),),
                decimal_places=4,
                default_currency="USD",
                max_digits=19,
                validators=[djmoney.models.validators.MinMoneyValidator(0)],
                verbose_name="price",
            ),
        ),
    ]
