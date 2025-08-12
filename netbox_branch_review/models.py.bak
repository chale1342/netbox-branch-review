from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import reverse
from netbox.models import NetBoxModel
from .choices import CRStatusChoices

try:
    from netbox_branching.models.branches import Branch
except Exception:
    Branch = None

User = get_user_model()

class ChangeRequest(NetBoxModel):
    title = models.CharField(max_length=200)
    summary = models.TextField(blank=True)
    requested_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="change_requests_created")
    status = models.CharField(max_length=32, choices=CRStatusChoices, default=CRStatusChoices.PENDING)
    planned_start = models.DateTimeField(null=True, blank=True)
    planned_end = models.DateTimeField(null=True, blank=True)
    risk = models.CharField(max_length=64, blank=True)
    impact = models.CharField(max_length=64, blank=True)
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
        )

    def get_absolute_url(self):
        return reverse("plugins:netbox_branch_review:changerequest", args=[self.pk])

    def __str__(self):
        return f"CR#{self.pk}: {self.title}"

    def approvers_required(self):
        from django.conf import settings
        return 2 if settings.PLUGINS_CONFIG.get("netbox_branch_review", {}).get("require_two_approvals", True) else 1
