from netbox.forms import NetBoxModelForm
from .models import ChangeRequest
from django import forms

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
            "title", "summary",
            "ticket",
            "risk", "impact", "branch",
            "planned_start", "planned_end",
        )
        widgets = {
            "planned_start": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "planned_end": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        # Ensure branch optional; risk initial blank
        if 'risk' in self.fields:
            self.fields['risk'].initial = ''
        # Remove tags if NetBoxModelForm injected it
        self.fields.pop('tags', None)
        # Capitalize Start/End labels
        if 'planned_start' in self.fields:
            self.fields['planned_start'].label = 'Planned Start'
        if 'planned_end' in self.fields:
            self.fields['planned_end'].label = 'Planned End'

    def save(self, commit=True):
        obj = super().save(commit=False)
        # Set requester to current user if available and not already set
        if not obj.pk and self.request and self.request.user and self.request.user.is_authenticated:
            obj.requested_by = self.request.user
        # Force status to pending on creation
        if not obj.pk:
            from .choices import CRStatusChoices
            obj.status = CRStatusChoices.PENDING
        if commit:
            obj.save()
            self.save_m2m()
        return obj