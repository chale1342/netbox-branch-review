import django_tables2 as tables
from netbox.tables import NetBoxTable
from .models import ChangeRequest

class ChangeRequestTable(NetBoxTable):
    title = tables.Column(linkify=True)
    status = tables.Column()

    class Meta(NetBoxTable.Meta):
        model = ChangeRequest
        fields = (
            "pk", "id", "title", "status", "requested_by",
            "planned_start", "planned_end", "branch", "created",
        )
        default_columns = ("id", "title", "status", "requested_by", "branch", "created")