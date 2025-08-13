from django.conf import settings
from django.db import migrations, models
import taggit.managers
import django.db.models.deletion
import utilities.json


class Migration(migrations.Migration):
    """Squashed initial migration for unreleased plugin.

    Consolidates prior incremental migrations (0001-0008) into a single
    authoritative schema baseline.
    """

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("contenttypes", "0002_remove_content_type_name"),
        ("netbox_branching", "0001_initial"),
        (
            "extras",
            "0129_fix_script_paths",
        ),  # ensure Tag/TaggedItem & JSON encoder ready
    ]

    operations = [
        migrations.CreateModel(
            name="ChangeRequest",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                ("title", models.CharField(max_length=200)),
                ("summary", models.TextField(blank=True)),
                # Added in 0002 for PrimaryModel compatibility; kept separate to avoid breaking existing deployments
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
                (
                    "ticket",
                    models.CharField(
                        blank=True,
                        max_length=100,
                        help_text="External ticket or issue reference",
                    ),
                ),
                ("object_id", models.PositiveIntegerField(blank=True, null=True)),
                ("approver_1_at", models.DateTimeField(blank=True, null=True)),
                ("approver_2_at", models.DateTimeField(blank=True, null=True)),
                # NetBoxModel contributes custom_field_data; include DB column here
                (
                    "custom_field_data",
                    models.JSONField(
                        blank=True,
                        default=dict,
                        encoder=utilities.json.CustomFieldJSONEncoder,
                    ),
                ),
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
                (
                    "tags",
                    taggit.managers.TaggableManager(
                        through="extras.TaggedItem", to="extras.Tag"
                    ),
                ),
            ],
            options={
                "ordering": ("-created",),
                "permissions": (
                    ("approve_changerequest", "Can approve change request"),
                    ("merge_changerequest", "Can merge branch for change request"),
                    ("peer_review_changerequest", "Can peer review change request"),
                    ("revoke_changerequest", "Can revoke approvals on change request"),
                ),
            },
        ),
        migrations.CreateModel(
            name="ChangeRequestAudit",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "change_request",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="audit_logs",
                        to="netbox_branch_review.changerequest",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="change_request_audits",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "action",
                    models.CharField(
                        choices=[
                            ("approve_level1", "First approval"),
                            ("approve_level2", "Second approval"),
                            ("peer_review", "Peer review"),
                            ("merge", "Merge / implement"),
                            ("double_approval_blocked", "Blocked duplicate approval"),
                            ("revoke_level1", "Revoke first approval"),
                            ("revoke_level2", "Revoke second approval"),
                            ("revoke_full", "Revoke full approval"),
                        ],
                        max_length=32,
                    ),
                ),
                ("message", models.TextField(blank=True)),
                ("created", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ("-created",)},
        ),
    ]
