import django_tables2 as tables
from netbox.tables import NetBoxTable
from .models import ChangeRequest

class ChangeRequestTable(NetBoxTable):
    title = tables.Column(linkify=True)

    class Meta(NetBoxTable.Meta):
        model = ChangeRequest
        fields = ("id", "title", "status", "branch", "requested_by", "last_updated")
        default_columns = ("id", "title", "status", "branch", "requested_by", "last_updated")
