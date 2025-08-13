from django.core.exceptions import ValidationError  # kept if needed elsewhere
from django.conf import settings  # noqa: F401
from .models import ChangeRequest, CRStatusChoices

try:
    from netbox_branching.models.branches import BranchActionIndicator  # type: ignore
except Exception:

    class BranchActionIndicator:  # minimal fallback
        def __init__(self, permitted: bool, message: str = ""):
            self.permitted = permitted
            self.message = message

        def __bool__(self):
            return self.permitted


def require_cr_approved_before_merge(branch):
    """Return BranchActionIndicator permitting merge only if related CR approved."""
    qs = ChangeRequest.objects.filter(branch_id=branch.pk)
    if not qs.exists():
        return BranchActionIndicator(False, "No Change Request for branch")
    latest = qs.order_by("-pk").first()
    if qs.filter(
        status__in=[CRStatusChoices.APPROVED, CRStatusChoices.IMPLEMENTED]
    ).exists():
        return BranchActionIndicator(True)
    return BranchActionIndicator(
        False, f"Change Request {latest.pk} not approved (status={latest.status})"
    )
