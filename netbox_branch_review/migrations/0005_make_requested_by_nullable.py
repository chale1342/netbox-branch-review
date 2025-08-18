"""Make requested_by nullable to allow anonymous or system-created CRs

Revision ID: 0005_make_requested_by_nullable
Revises: 0004_add_comments
Create Date: 2025-08-18 14:50
"""
from django.db import migrations, models
from django.conf import settings

class Migration(migrations.Migration):

    dependencies = [
        ("netbox_branch_review", "0004_add_comments"),
    ]

    operations = [
        migrations.AlterField(
            model_name="changerequest",
            name="requested_by",
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=models.PROTECT,
                related_name="change_requests_created",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
