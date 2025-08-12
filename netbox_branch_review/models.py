from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import reverse
from netbox.models import PrimaryModel
from .choices import CRStatusChoices

try:
    from netbox_branching.models.branches import Branch
except Exception:
    Branch = None

User = get_user_model()

class ChangeRequest(PrimaryModel):
    title = models.CharField(max_length=200)
    summary = models.TextField(blank=True)
    description = models.CharField(max_length=200, blank=True)
    comments = models.TextField(blank=True)
    requested_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="change_requests_created")
    status = models.CharField(max_length=32, choices=CRStatusChoices, default=CRStatusChoices.PENDING)
    planned_start = models.DateTimeField(null=True, blank=True)
    planned_end = models.DateTimeField(null=True, blank=True)
    risk = models.CharField(max_length=64, blank=True)
    impact = models.CharField(max_length=64, blank=True)
    ticket = models.CharField(max_length=100, blank=True, help_text="External ticket or issue reference")
    object_type = models.ForeignKey(ContentType, on_delete=models.PROTECT, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    target = GenericForeignKey("object_type", "object_id")
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name="change_requests", null=True, blank=True)
    approver_1 = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True, related_name="change_requests_approved_lvl1")
    approver_1_at = models.DateTimeField(null=True, blank=True)
    approver_2 = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True, related_name="change_requests_approved_lvl2")
    approver_2_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created",)
        permissions = (
            ("approve_changerequest", "Can approve change request"),
            ("merge_changerequest", "Can merge branch for change request"),
            ("peer_review_changerequest", "Can peer review change request"),
            ("revoke_changerequest", "Can revoke approvals on change request"),
        )

    def get_absolute_url(self):
        return reverse("plugins:netbox_branch_review:changerequest", args=[self.pk])

    def __str__(self):
        return f"CR#{self.pk}: {self.title}"

    def approvers_required(self):
        from django.conf import settings
        return 2 if settings.PLUGINS_CONFIG.get("netbox_branch_review", {}).get("require_two_approvals", True) else 1

    def get_changelog_url(self):
        return None

    def get_journal_url(self):
        return None

    @property
    def changelog_url(self):
        return None

    @property
    def journal_url(self):
        return None


class ChangeRequestAudit(models.Model):
    ACTION_CHOICES = (
        ("approve_level1", "First approval"),
        ("approve_level2", "Second approval"),
        ("peer_review", "Peer review"),
        ("merge", "Merge / implement"),
        ("double_approval_blocked", "Blocked duplicate approval"),
    ("revoke_level1", "Revoke first approval"),
    ("revoke_level2", "Revoke second approval"),
    ("revoke_full", "Revoke full approval"),
    )
    change_request = models.ForeignKey(ChangeRequest, on_delete=models.CASCADE, related_name="audit_logs")
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="change_request_audits")
    action = models.CharField(max_length=32, choices=ACTION_CHOICES)
    message = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created",)

    def __str__(self):
        return f"CR#{self.change_request_id} {self.action} by {self.user} @ {self.created}"
