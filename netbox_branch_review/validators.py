from django.core.exceptions import ValidationError

def require_cr_approved_before_merge(branch, user, action: str):
    if action != "merge":
        return
    from .models import ChangeRequest
    qs = ChangeRequest.objects.filter(branch=branch).order_by("-created")
    if not qs.exists():
        raise ValidationError("Branch has no associated ChangeRequest.")
    cr = qs.first()
    if cr.approvers_required() == 2 and not (cr.approver_1 and cr.approver_2):
        raise ValidationError("Two approvals required before merge.")
    if cr.status not in ("approved", "scheduled"):
        raise ValidationError("ChangeRequest must be approved or scheduled before merge.")
