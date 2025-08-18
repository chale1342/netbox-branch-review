from netbox.api.viewsets import NetBoxModelViewSet
from ..models import ChangeRequest
from .serializers import ChangeRequestSerializer

class ChangeRequestViewSet(NetBoxModelViewSet):
    queryset = ChangeRequest.objects.all()
    serializer_class = ChangeRequestSerializer

    def perform_create(self, serializer):
        # Ensure the requesting user becomes the requested_by for new change requests
        serializer.save(requested_by=self.request.user)