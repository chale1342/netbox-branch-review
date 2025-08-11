import django_filters
from netbox.filtersets import NetBoxModelFilterSet
from .models import ChangeRequest

class ChangeRequestFilterSet(NetBoxModelFilterSet):
    q = django_filters.CharFilter(method="search", label="Search")

    class Meta:
        model = ChangeRequest
        fields = ("status", "requested_by", "approver_1", "approver_2", "branch")

    def search(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(title__icontains=value)