from netbox.api.viewsets import NetBoxModelViewSet
from ..models import ChangeRequest
from .serializers import ChangeRequestSerializer

class ChangeRequestViewSet(NetBoxModelViewSet):
    queryset = ChangeRequest.objects.all()
    serializer_class = ChangeRequestSerializer