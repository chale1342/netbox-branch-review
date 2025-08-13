# Netbox-Branch-Review
Branch-aware change request & approval workflow for NetBox that can gate branch merges until a Change Request (CR) is approved.

- Model: [`netbox_branch_review.models.ChangeRequest`](netbox_branch_review/models.py)
- Status choices: [`netbox_branch_review.choices.CRStatusChoices`](netbox_branch_review/choices.py)
- UI views: [`netbox_branch_review.views`](netbox_branch_review/views.py)
- Merge gate validator: [`netbox_branch_review.validators.require_cr_approved_before_merge`](netbox_branch_review/validators.py)
- API: [`netbox_branch_review.api.views.ChangeRequestViewSet`](netbox_branch_review/api/views.py), [`netbox_branch_review.api.serializers.ChangeRequestSerializer`](netbox_branch_review/api/serializers.py)
- Plugin config: [`netbox_branch_review.__init__.BranchReviewConfig`](netbox_branch_review/__init__.py)

## Features
- Create and track Change Requests linked to branches
- One- or two-level approvals (configurable)
- Merge gate: blocks merges until CR is approved or scheduled
- Simple UI actions: Approve and Merge from the CR detail page
- API serializers/viewset for integration
- Optional peer review action & audit log of approvals / merge events
 - Revoke (undo) approvals before implementation, resetting status to Pending

## Requirements
- NetBox 4.x
- Netbox-Branching plugin for branch operations (the merge gate integrates with it)
- Python 3.10+

## Installation
1) Install the plugin:
```sh
pip install netbox-branch-review 
```

2) Enable in NetBox configuration.py:
```python
PLUGINS = [
    "netbox_branch_review",
    "netbox_branching",
]

PLUGINS_CONFIG = {
    "netbox_branch_review": {
        # Require two approvals before merge (default: True)
        "require_two_approvals": True,
        # Enforce branching integration (default: True)
        "enforce_branching": True,
    # Approval implies branch changes are acceptable; merge button appears once approved.
    }
}
```

3) Migrate:
```sh
python manage.py migrate
```

4) Restart NetBox.

### Quick Start (Groups & Permissions)
Run the management command to create/sync default groups and permissions:
```bash
python manage.py sync_change_review
```
This will ensure:
- Group "Change Managers" gets approve / merge / peer review permissions.
- Group "Change Reviewers" gets only the peer review permission.

Customize names:
```bash
python manage.py sync_change_review --managers "My Managers" --reviewers "My Reviewers"
```
Skip peer group creation:
```bash
python manage.py sync_change_review --no-peer-group
```

## Usage
- Navigate to Plugins → Change Requests (menu declared in [`menu.py`](netbox_branch_review/menu.py))
- Create a CR (form: [`ChangeRequestForm`](netbox_branch_review/forms.py))
- The CR form includes an optional Ticket field for referencing external systems.
- From the CR page, Approve and Merge using the actions in the header
  - Template: [`templates/.../includes/changerequest_header.html`](netbox_branch_review/templates/netbox_branch_review/includes/changerequest_header.html)

### Approval & Peer Review Flow
Config key: `require_two_approvals` (default True)
Self full approval: `allow_self_full_approval` (default True) lets the CR creator (who has approval permission) fully approve in one action even when two approvals are normally required (records both levels in audit with an implicit second approval entry).

| Scenario | Action 1 | Action 2 | Status progression |
|----------|----------|----------|--------------------|
| Two approvals required | First approval (different user recorded, or creator self-approval if allowed) | Second approval (must be different user unless self full approval triggered) | Pending → In review → Approved (or direct to Approved if self full) |
| Single approval mode | First approval | (Further approvals blocked for same user) | Pending → Approved |

Peer Review (optional): A user with only `peer_review_changerequest` can record a peer review before approval. Peer reviews do NOT change status; they are logged for audit & visibility.

Merge sets status to “Implemented”. Duplicate approvals or attempts after final approval are logged and safely ignored.

The merge gate validator [`require_cr_approved_before_merge`](netbox_branch_review/validators.py) enforces:
- Two approvals when configured
- Status must be Approved or Scheduled

## Permissions & Suggested Groups
Custom permissions defined on the model: [`ChangeRequest.Meta.permissions`](netbox_branch_review/models.py)

| Codename | Purpose |
|----------|---------|
| approve_changerequest | Perform L1/L2 approvals (depending on config) |
| merge_changerequest | Execute merge / implement action |
| peer_review_changerequest | Record a peer review (no status change) |
| revoke_changerequest | Revoke existing approvals (pre-implementation) |

Because NetBox’s Group UI currently only lists standard model permissions in the multiselect, custom codenames may not appear for manual selection. The plugin’s `post_migrate` signal ensures they are created; you can assign them via shell if needed.

Suggested groups:
- Change Managers: `approve_changerequest`, `merge_changerequest` (optionally also `peer_review_changerequest`).
- Change Reviewers: `peer_review_changerequest` (and `view_changerequest` if not already provided globally).

Example shell assignment:
```bash
python manage.py shell -c "from django.contrib.auth.models import Group,Permission; mgr,_=Group.objects.get_or_create(name='Change Managers'); rev,_=Group.objects.get_or_create(name='Change Reviewers'); mgr.permissions.add(*Permission.objects.filter(codename__in=['approve_changerequest','merge_changerequest','peer_review_changerequest'])); rev.permissions.add(Permission.objects.get(codename='peer_review_changerequest'))"
```

Check a user’s effective perms:
```bash
python manage.py shell -c "from django.contrib.auth import get_user_model; u=get_user_model().objects.get(username='alice'); print([p for p in sorted(u.get_all_permissions()) if p.startswith('netbox_branch_review.')])"
```

## Audit Log
Each approval, peer review, merge, revoke, or blocked duplicate attempt writes an entry to `ChangeRequestAudit` (displayed on the CR detail page). The last 10 entries render as badges; extend as needed.

### Revoking Approvals (Undo)
Users with `revoke_changerequest` can revert a Change Request back to Pending (prior to implementation). This:
1. Creates audit entries for each revoked level (L2 then L1) plus a summary revoke_full entry.
2. Clears `approver_1`, `approver_2` and their timestamps.
3. Sets status to `pending`.

Limitations:
- Can't revoke after status reaches Implemented.
- Self full approvals (implicit level 2) will be fully cleared in one revoke action.

UI: A Revoke Approvals button appears when (a) the user has the permission, (b) the CR isn't implemented, and (c) at least one approval exists.

## API
- Serializer: [`ChangeRequestSerializer`](netbox_branch_review/api/serializers.py)
- ViewSet: [`ChangeRequestViewSet`](netbox_branch_review/api/views.py)

Note: Expose routes via the NetBox plugin API router as needed. The serializer exposes all CR fields, including ticket.

## Project layout
```
netbox-branch-review/
├── pyproject.toml
├── README.md
└── netbox_branch_review/
    ├── __init__.py
    # (plugin.py not used; configuration lives in __init__.py)
    ├── models.py
    ├── choices.py
    ├── forms.py
    ├── filtersets.py
    ├── tables.py
    ├── navigation.py
    ├── menu.py
    ├── urls.py
    ├── views.py
    ├── signals.py
    ├── validators.py
    ├── api/
    │   ├── __init__.py
    │   ├── serializers.py
    │   └── views.py
    ├── templates/
    │   └── netbox_branch_review/
    │       ├── changerequest_list.html
    │       ├── changerequest.html
    │       └── includes/
    │           └── changerequest_header.html
    └── migrations/
    ├── 0001_initial.py
    ├── 0002_add_description.py
    ├── 0003_merge.py
    └── 0004_add_comments.py
```

## Notes
- The plugin registers the merge gate during `ready()` by calling `register_pre_merge_validator()` if available (see [`__init__.py`](netbox_branch_review/__init__.py)). If the branching plugin is not present, merge enforcement gracefully no-ops, and UI will warn when branch data
- Default groups may also be auto-created during `post_migrate` based on plugin settings (see `__init__.py` and `signals.py`), but the management command provides a clear, repeatable onboarding step.