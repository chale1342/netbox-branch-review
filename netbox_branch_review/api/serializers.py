from rest_framework import serializers
from ..models import ChangeRequest

class ChangeRequestSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_branch_review-api:changerequest-detail")

    class Meta:
        model = ChangeRequest
        fields = [
            "id", "url", "title", "summary", "requested_by", "status",
            "planned_start", "planned_end", "risk", "impact", "branch",
            "object_type", "object_id", "created", "last_updated",
            "approver_1", "approver_1_at", "approver_2", "approver_2_at",
        ]