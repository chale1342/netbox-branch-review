# netbox-branch-review
Branch-aware merge approval system for NetBox that gates branch merges until a Change Request (CR) is approved.

- Model: [`netbox_branch_review.models.ChangeRequest`](netbox_branch_review/models.py)
- Status choices: [`netbox_branch_review.choices.CRStatusChoices`](netbox_branch_review/choices.py)
- UI views: [`netbox_branch_review.views`](netbox_branch_review/views.py)
- Merge gate validator: [`netbox_branch_review.validators.require_cr_approved_before_merge`](netbox_branch_review/validators.py)
- API: [`netbox_branch_review.api.views.ChangeRequestViewSet`](netbox_branch_review/api/views.py), [`netbox_branch_review.api.serializers.ChangeRequestSerializer`](netbox_branch_review/api/serializers.py)
- Plugin config: [`netbox_branch_review.plugin.BranchReviewConfig`](netbox_branch_review/plugin.py)

## Features
- Create and track Change Requests linked to branches
- One- or two-level approvals (configurable)
- Merge gate: blocks merges until CR is approved or scheduled
- Simple UI actions: Approve and Merge from the CR detail page
- API serializers/viewset for integration

## Requirements
- NetBox 4.x
- Optional: netbox-branching plugin for branch operations (the merge gate integrates with it)
- Python 3.10+

## Installation
1) Install the plugin (editable install during development):
```sh
pip install -e .
```

2) Enable in NetBox configuration.py:
```python
PLUGINS = [
    # If using branch enforcement:
    "netbox_branching",
    "netbox_branch_review",
]

PLUGINS_CONFIG = {
    "netbox_branch_review": {
        # Require two approvals before merge (default: True)
        "require_two_approvals": True,
        # Enforce branching integration (default: True)
        "enforce_branching": True,
    }
}
```

3) Migrate:
```sh
python manage.py migrate
```

4) Restart NetBox.

## Usage
- Navigate to Plugins → Change Requests (menu declared in [`navigation.py`](netbox_branch_review/navigation.py))
- Create a CR (form: [`ChangeRequestForm`](netbox_branch_review/forms.py))
- From the CR page, Approve and Merge using the actions in the header
  - Template: [`templates/.../includes/changerequest_header.html`](netbox_branch_review/templates/netbox_branch_review/includes/changerequest_header.html)

### Approval flow
- First approval sets status to “In review”
- Second approval (if required) sets status to “Approved”
- Merge sets status to “Implemented”

The merge gate validator [`require_cr_approved_before_merge`](netbox_branch_review/validators.py) enforces:
- Two approvals when configured
- Status must be Approved or Scheduled

## Permissions
Grant users or groups:
- `netbox_branch_review.approve_changerequest`
- `netbox_branch_review.merge_changerequest`

Defined on the model: [`ChangeRequest.Meta.permissions`](netbox_branch_review/models.py).

## API
- Serializer: [`ChangeRequestSerializer`](netbox_branch_review/api/serializers.py)
- ViewSet: [`ChangeRequestViewSet`](netbox_branch_review/api/views.py)

Note: Expose routes via the NetBox plugin API router as needed.

## Project layout
```
netbox-branch-review/
├── pyproject.toml
├── README.md
└── netbox_branch_review/
    ├── __init__.py
    ├── plugin.py
    ├── models.py
    ├── choices.py
    ├── forms.py
    ├── filtersets.py
    ├── tables.py
    ├── navigation.py
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
        └── 0001_initial.py
```

## Notes
- The plugin registers the merge gate during `ready()` by calling `register_pre_action_validator()` if available (see [`plugin.py`](netbox_branch_review/plugin.py)). If the branching plugin is not present, merge enforcement gracefully no-ops, and UI will warn when branch data