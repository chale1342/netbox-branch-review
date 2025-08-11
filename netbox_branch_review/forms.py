from netbox.forms import NetBoxModelForm
from .models import ChangeRequest

class ChangeRequestForm(NetBoxModelForm):
    class Meta:
        model = ChangeRequest
        fields = (
            "title", "summary", "requested_by", "status",
            "planned_start", "planned_end", "risk", "impact",
            "object_type", "object_id", "branch",
        )