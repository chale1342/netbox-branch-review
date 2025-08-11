from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("contenttypes", "0002_remove_content_type_name"),
        ("netbox_branching", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ChangeRequest",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(max_length=200)),
                ("summary", models.TextField(blank=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("in_review", "In review"),
                            ("approved", "Approved"),
                            ("rejected", "Rejected"),
                            ("scheduled", "Scheduled"),
                            ("implemented", "Implemented"),
                            ("cancelled", "Cancelled"),
                        ],
                        default="pending",
                        max_length=32,
                    ),
                ),
                ("planned_start", models.DateTimeField(blank=True, null=True)),
                ("planned_end", models.DateTimeField(blank=True, null=True)),
                ("risk", models.CharField(blank=True, max_length=64)),
                ("impact", models.CharField(blank=True, max_length=64)),
                ("object_id", models.PositiveIntegerField(blank=True, null=True)),
                ("approver_1_at", models.DateTimeField(blank=True, null=True)),
                ("approver_2_at", models.DateTimeField(blank=True, null=True)),
                (
                    "object_type",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="contenttypes.contenttype",
                    ),
                ),
                (
                    "requested_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="change_requests_created",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "approver_1",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="change_requests_approved_lvl1",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "approver_2",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="change_requests_approved_lvl2",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "branch",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="change_requests",
                        to="netbox_branching.branch",
                    ),
                ),
            ],
            options={"ordering": ("-created",)},
        ),
    ]