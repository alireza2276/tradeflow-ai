from django.db import migrations, models


LEGACY_RULE_REFERENCE = "LEGACY-6M-9M-BACKFILL"


def backfill_regulatory_fields(apps, schema_editor):
    RegistrationOrder = apps.get_model(
        "trade_orders",
        "RegistrationOrder",
    )

    CurrencyPurchase = apps.get_model(
        "trade_orders",
        "CurrencyPurchase",
    )

    for order in RegistrationOrder.objects.select_related(
        "company"
    ).iterator():
        company_type = getattr(
            order.company,
            "company_type",
            None,
        )

        update_fields = []

        if not order.activity_type and company_type:
            order.activity_type = company_type
            update_fields.append("activity_type")

        if order.shipment_deadline_months is None:
            if company_type == "COMMERCIAL":
                order.shipment_deadline_months = 6
                update_fields.append(
                    "shipment_deadline_months"
                )

            elif company_type == "PRODUCTION":
                order.shipment_deadline_months = 9
                update_fields.append(
                    "shipment_deadline_months"
                )

        if not order.regulatory_rule_reference:
            order.regulatory_rule_reference = (
                LEGACY_RULE_REFERENCE
            )
            update_fields.append(
                "regulatory_rule_reference"
            )

        if update_fields:
            order.save(
                update_fields=update_fields
            )

    for purchase in CurrencyPurchase.objects.iterator():
        update_fields = []

        if purchase.remittance_date is None:
            purchase.remittance_date = (
                purchase.purchase_date
            )
            update_fields.append(
                "remittance_date"
            )

        if purchase.original_deadline is None:
            purchase.original_deadline = (
                purchase.deadline
            )
            update_fields.append(
                "original_deadline"
            )

        if update_fields:
            purchase.save(
                update_fields=update_fields
            )


def reverse_backfill_regulatory_fields(
    apps,
    schema_editor,
):
    RegistrationOrder = apps.get_model(
        "trade_orders",
        "RegistrationOrder",
    )

    CurrencyPurchase = apps.get_model(
        "trade_orders",
        "CurrencyPurchase",
    )

    RegistrationOrder.objects.filter(
        regulatory_rule_reference=(
            LEGACY_RULE_REFERENCE
        )
    ).update(
        regulatory_rule_reference="",
    )

    CurrencyPurchase.objects.update(
        original_deadline=None,
        remittance_date=None,
    )


class Migration(migrations.Migration):

    dependencies = [
        (
            "trade_orders",
            (
                "0008_alter_shipmentpart_options_"
                "shipmentpart_is_void_and_more"
            ),
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="currencypurchase",
            name="deadline_extension_reason",
            field=models.TextField(
                blank=True,
            ),
        ),

        migrations.AddField(
            model_name="currencypurchase",
            name="deadline_extension_reference",
            field=models.CharField(
                blank=True,
                max_length=120,
            ),
        ),

        migrations.AddField(
            model_name="currencypurchase",
            name="original_deadline",
            field=models.DateField(
                blank=True,
                null=True,
            ),
        ),

        migrations.AddField(
            model_name="currencypurchase",
            name="remittance_date",
            field=models.DateField(
                blank=True,
                null=True,
                help_text=(
                    "Date the FX remittance was issued. "
                    "For remittance imports, the "
                    "shipping-document deadline is "
                    "measured from this date."
                ),
            ),
        ),

        migrations.AddField(
            model_name="registrationorder",
            name="activity_type",
            field=models.CharField(
                blank=True,
                null=True,
                max_length=20,
                choices=[
                    (
                        "COMMERCIAL",
                        "Commercial",
                    ),
                    (
                        "PRODUCTION",
                        "Production",
                    ),
                ],
                help_text=(
                    "Snapshot of the activity type "
                    "recorded on the registration order. "
                    "Regulatory deadlines must use this "
                    "value rather than the company's "
                    "current master-data type."
                ),
            ),
        ),

        migrations.AddField(
            model_name="registrationorder",
            name="regulatory_rule_reference",
            field=models.CharField(
                blank=True,
                max_length=120,
                help_text=(
                    "CBI circular / Part One / table "
                    "or clause reference."
                ),
            ),
        ),

        migrations.AddField(
            model_name="registrationorder",
            name="shipment_deadline_months",
            field=models.PositiveSmallIntegerField(
                blank=True,
                null=True,
                help_text=(
                    "Maximum shipping-document deadline "
                    "applicable to this registration "
                    "order under the current CBI "
                    "rule/table."
                ),
            ),
        ),

        migrations.AlterField(
            model_name="currencypurchase",
            name="purchase_date",
            field=models.DateField(
                help_text=(
                    "Currency funding/purchase date."
                ),
            ),
        ),

        migrations.RunPython(
            backfill_regulatory_fields,
            reverse_backfill_regulatory_fields,
        ),
    ]