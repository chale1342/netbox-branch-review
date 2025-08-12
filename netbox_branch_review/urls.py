from django.urls import path
from . import views

app_name = "netbox_branch_review"

urlpatterns = [
    path("", views.ChangeRequestListView.as_view(), name="changerequest_list"),
    path("add/", views.ChangeRequestEditView.as_view(), name="changerequest_add"),
    path("<int:pk>/", views.ChangeRequestView.as_view(), name="changerequest"),
    path("<int:pk>/edit/", views.ChangeRequestEditView.as_view(), name="changerequest_edit"),
    path("<int:pk>/approve/", views.ChangeRequestApproveView.as_view(), name="changerequest_approve"),
    path("<int:pk>/merge/", views.ChangeRequestMergeView.as_view(), name="changerequest_merge"),
    path("<int:pk>/peer-review/", views.ChangeRequestPeerReviewView.as_view(), name="changerequest_peer_review"),
    path("<int:pk>/revoke/", views.ChangeRequestRevokeView.as_view(), name="changerequest_revoke"),
    path("<int:pk>/delete/", views.ChangeRequestDeleteView.as_view(), name="changerequest_delete"),
]
