from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views import View
from django.http import Http404
from django.conf import settings
from netbox.views import generic
from .models import ChangeRequest, ChangeRequestAudit
from .tables import ChangeRequestTable
from .forms import ChangeRequestForm
from .filtersets import ChangeRequestFilterSet

try:
    from netbox_branching.models.branches import Branch
except Exception:
    Branch = None


class ChangeRequestListView(generic.ObjectListView):
    queryset = ChangeRequest.objects.all()
    table = ChangeRequestTable
    filterset = ChangeRequestFilterSet


class ChangeRequestView(generic.ObjectView):
    queryset = ChangeRequest.objects.all()

    def get_extra_context(self, request, instance):
        changes = []
        try:
            if instance.branch and Branch:
                # Attempt to fetch unmerged changes from branching plugin
                changes = instance.branch.get_unmerged_changes()
        except Exception:
            changes = []
        return {
            "unmerged_changes": changes,
            "unmerged_changes_count": len(changes),
        }


class ChangeRequestEditView(generic.ObjectEditView):
    queryset = ChangeRequest.objects.all()
    form = ChangeRequestForm


class ChangeRequestApproveView(PermissionRequiredMixin, View):
    permission_required = "netbox_branch_review.approve_changerequest"

    def post(self, request, pk):
        cr = get_object_or_404(ChangeRequest, pk=pk)
        now = timezone.now()

        # Prevent the same user from supplying both approvals when two are required (unless self-full allowed)
        if (
            cr.approver_1
            and cr.approver_1 == request.user
            and cr.approvers_required() == 2
            and not cr.approver_2
        ):
            # We still allow if self full approval will immediately mark approved (handled below before second check)
            pass

        required = cr.approvers_required()
        allow_self_full = settings.PLUGINS_CONFIG.get("netbox_branch_review", {}).get(
            "allow_self_full_approval", True
        )

        # Block duplicate in single-approval mode
        if required == 1 and cr.approver_1 and cr.approver_1 == request.user:
            messages.info(request, "You have already approved this change request.")
            ChangeRequestAudit.objects.create(
                change_request=cr,
                user=request.user,
                action="double_approval_blocked",
                message="Duplicate single approval attempt",
            )
            return redirect(cr.get_absolute_url())

        if not cr.approver_1:
            # First approval
            cr.approver_1 = request.user
            cr.approver_1_at = now
            if required == 1 or (
                required == 2
                and allow_self_full
                and cr.requested_by_id == request.user.id
            ):
                # Self full approval path (records level2 implicitly)
                if (
                    required == 2
                    and allow_self_full
                    and cr.requested_by_id == request.user.id
                ):
                    cr.approver_2 = request.user
                    cr.approver_2_at = now
                cr.status = "approved"
            else:
                cr.status = "in_review"
            messages.success(request, "First approval recorded.")
            ChangeRequestAudit.objects.create(
                change_request=cr, user=request.user, action="approve_level1"
            )
            if cr.status == "approved" and cr.approver_2_id == request.user.id:
                ChangeRequestAudit.objects.create(
                    change_request=cr,
                    user=request.user,
                    action="approve_level2",
                    message="Implicit self second approval",
                )
        elif required == 2 and not cr.approver_2:
            # Second approval (must be different user unless self full already handled)
            if cr.approver_1_id == request.user.id:
                messages.warning(
                    request, "Second (peer) approval must be a different user."
                )
                ChangeRequestAudit.objects.create(
                    change_request=cr,
                    user=request.user,
                    action="double_approval_blocked",
                    message="Attempted second approval by same user",
                )
                return redirect(cr.get_absolute_url())
            cr.approver_2 = request.user
            cr.approver_2_at = now
            cr.status = "approved"
            messages.success(
                request, "Second approval recorded. Change request is now approved."
            )
            ChangeRequestAudit.objects.create(
                change_request=cr, user=request.user, action="approve_level2"
            )
        else:
            messages.info(request, "Change request already approved.")
            ChangeRequestAudit.objects.create(
                change_request=cr,
                user=request.user,
                action="double_approval_blocked",
                message="Approval after fully approved",
            )

        cr.save()
        return redirect(cr.get_absolute_url())


class ChangeRequestMergeView(PermissionRequiredMixin, View):
    permission_required = "netbox_branch_review.merge_changerequest"

    def post(self, request, pk):
        cr = get_object_or_404(ChangeRequest, pk=pk)
        if not Branch or not cr.branch_id:
            messages.error(request, "Branching plugin unavailable or branch missing.")
            return redirect(cr.get_absolute_url())
        branch = cr.branch
        try:
            branch.merge(request.user, commit=True)
            cr.status = "implemented"
            cr.save()
            messages.success(request, "Branch merged and change implemented.")
            ChangeRequestAudit.objects.create(
                change_request=cr, user=request.user, action="merge"
            )
        except Exception as exc:
            messages.error(request, f"Merge failed: {exc}")
        return redirect(cr.get_absolute_url())


class ChangeRequestPeerReviewView(PermissionRequiredMixin, View):
    permission_required = "netbox_branch_review.peer_review_changerequest"

    def post(self, request, pk):
        cr = get_object_or_404(ChangeRequest, pk=pk)
        # Only allow peer review before fully approved / implemented
        if cr.status in ("approved", "implemented"):
            messages.info(request, "Peer review not needed; already approved.")
            return redirect(cr.get_absolute_url())
        ChangeRequestAudit.objects.create(
            change_request=cr, user=request.user, action="peer_review"
        )
        messages.success(request, "Peer review recorded.")
        return redirect(cr.get_absolute_url())


class ChangeRequestRevokeView(PermissionRequiredMixin, View):
    permission_required = "netbox_branch_review.revoke_changerequest"

    def post(self, request, pk):
        cr = get_object_or_404(ChangeRequest, pk=pk)
        # Only revoke if not implemented
        if cr.status == "implemented":
            messages.error(request, "Cannot revoke after implementation.")
            return redirect(cr.get_absolute_url())

        # Determine what to revoke
        revoked_any = False
        if cr.approver_2:
            ChangeRequestAudit.objects.create(
                change_request=cr, user=request.user, action="revoke_level2"
            )
            cr.approver_2 = None
            cr.approver_2_at = None
            revoked_any = True
        if cr.approver_1:
            ChangeRequestAudit.objects.create(
                change_request=cr, user=request.user, action="revoke_level1"
            )
            cr.approver_1 = None
            cr.approver_1_at = None
            revoked_any = True

        if revoked_any:
            cr.status = "pending"
            ChangeRequestAudit.objects.create(
                change_request=cr,
                user=request.user,
                action="revoke_full",
                message="Approvals reset to pending",
            )
            cr.save()
            messages.success(request, "Approvals revoked; status reset to pending.")
        else:
            messages.info(request, "No approvals to revoke.")
        return redirect(cr.get_absolute_url())


class ChangeRequestDeleteView(generic.ObjectDeleteView):
    queryset = ChangeRequest.objects.all()


class _PlaceholderView(View):
    """Return 404 for deprecated/disabled routes (changelog/journal)."""

    def get(self, request, *args, **kwargs):  # pragma: no cover - simple stub
        raise Http404()

    def post(self, request, *args, **kwargs):  # safety
        raise Http404()


# Exposed as class names for URLConf clarity
ChangeRequestChangelogView = _PlaceholderView
ChangeRequestJournalView = _PlaceholderView
