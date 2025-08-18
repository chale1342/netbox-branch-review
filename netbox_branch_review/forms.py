from netbox.forms import NetBoxModelForm
from .models import ChangeRequest
from django import forms
import threading

# Thread-local storage to provide request to forms when the view can't pass it via kwargs
_req_local = threading.local()

def set_current_request(request):  # used by views
    try:
        _req_local.request = request
    except Exception:
        _req_local.request = None

def get_current_request():
    return getattr(_req_local, "request", None)

RISK_CHOICES = [
    ("", "--------"),
    ("low", "Low"),
    ("medium", "Medium"),
    ("high", "High"),
    ("critical", "Critical"),
]


class ChangeRequestForm(NetBoxModelForm):
    risk = forms.ChoiceField(choices=RISK_CHOICES, required=False)

    class Meta:
        model = ChangeRequest
        # Exclude internal/auto fields: requested_by, status forced to pending, object mapping fields.
        fields = (
            "title",
            "summary",
            "ticket",
            "risk",
            "impact",
            "branch",
            "planned_start",
            "planned_end",
        )
        widgets = {
            "planned_start": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "planned_end": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None) or get_current_request()
        super().__init__(*args, **kwargs)
        # Ensure branch optional; risk initial blank
        if "risk" in self.fields:
            self.fields["risk"].initial = ""
        # Remove tags if NetBoxModelForm injected it
        self.fields.pop("tags", None)
        # Capitalize Start/End labels
        if "planned_start" in self.fields:
            self.fields["planned_start"].label = "Planned Start"
        if "planned_end" in self.fields:
            self.fields["planned_end"].label = "Planned End"

    def save(self, commit=True):
        obj = super().save(commit=False)
        # Set requester to current user if available and not already set
        if not obj.pk:
            # Prefer request.user, then thread-local, then NetBox's self.user (ObjectEditView sets this)
            requester = None
            req = self.request or get_current_request()
            try:
                if req and getattr(req, "user", None):
                    requester = req.user
            except Exception:
                requester = None
            if requester is None:
                requester = getattr(self, "user", None)
            try:
                if requester and getattr(requester, "is_authenticated", False) and not obj.requested_by_id:
                    obj.requested_by = requester
            except Exception:
                pass
        # Force status to pending on creation
        if not obj.pk:
            from .choices import CRStatusChoices

            obj.status = CRStatusChoices.PENDING
        if commit:
            obj.save()
            self.save_m2m()
        return obj
