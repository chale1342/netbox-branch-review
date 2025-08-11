from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from netbox.views import generic
from .models import ChangeRequest
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

class ChangeRequestEditView(generic.ObjectEditView):
    queryset = ChangeRequest.objects.all()
    form = ChangeRequestForm

class ChangeRequestApproveView(PermissionRequiredMixin, generic.View):
    permission_required = "netbox_branch_review.approve_changerequest"

    def post(self, request, pk):
        cr = get_object_or_404(ChangeRequest, pk=pk)
        now = timezone.now()
        if not cr.approver_1:
            cr.approver_1 = request.user
            cr.approver_1_at = now
            cr.status = "in_review"
        elif not cr.approver_2 and cr.approvers_required() == 2:
            cr.approver_2 = request.user
            cr.approver_2_at = now
            cr.status = "approved"
        else:
            cr.status = "approved"
        cr.save()
        messages.success(request, "Change request approved.")
        return redirect(cr.get_absolute_url())

class ChangeRequestMergeView(PermissionRequiredMixin, generic.View):
    permission_required = "netbox_branch_review.merge_changerequest"

    def post(self, request, pk):
        cr = get_object_or_404(ChangeRequest, pk=pk)
        if not Branch or not cr.branch_id:
            messages.error(request, "Branching plugin unavailable or branch missing.")
            return redirect(cr.get_absolute_url())
        branch = cr.branch
        try:
            unmerged = branch.get_unmerged_changes()
        except Exception:
            unmerged = []
        if unmerged:
            messages.error(request, "Unreviewed changes present; merge blocked.")
            return redirect(cr.get_absolute_url())
        try:
            branch.merge(request.user)
            cr.status = "implemented"
            cr.save()
            messages.success(request, "Branch merged and change implemented.")
        except Exception as exc:
            messages.error(request, f"Merge failed: {exc}")
        return redirect(cr.get_absolute_url())