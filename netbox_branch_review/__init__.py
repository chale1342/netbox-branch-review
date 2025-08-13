from netbox.plugins import PluginConfig
import logging

class BranchReviewConfig(PluginConfig):
    name = "netbox_branch_review"
    verbose_name = "Branch Review"
    # Short one-line summary (appears as Summary/Description in plugin UI)
    description = "Branch-aware change request & approval workflow"
    # Keep this in sync with pyproject.toml [project].version
        version = "0.1.8"  # Updated to version 0.1.8
    # Metadata for NetBox plugin registry page
    author = "Chris Hale"
    author_url = "https://github.com/chale1342/netbox-branch-review"
    license = "MIT"
    # Declare supported NetBox core version range (adjust as needed)
    min_version = "4.3.0"
    max_version = "5.0"
    base_url = "branch-review"
    default_settings = {
        "require_two_approvals": True,
        "auto_create_group": True,
        "auto_group_name": "Change Managers",
    # Auto-create a peer review group with only peer review permission
    "auto_peer_group_name": "Change Reviewers",
    # Allow creator to fully approve their own CR when two approvals required
    "allow_self_full_approval": True,
    # Troubleshooting flag: when True merge validator always allows commit
    "debug_always_allow_merge": False,
    # If True hide unmerged changes after approval
    "suppress_unmerged_after_approval": False,
    }

    def ready(self):
        super().ready()
        # register signal handlers
        from . import signals  # noqa: F401
        plugin_logger = logging.getLogger("netbox_branch_review")
        # Register merge validator with branching plugin if available
        try:
            from netbox_branching.registry import register_pre_merge_validator
            from .validators import require_cr_approved_before_merge
            register_pre_merge_validator(require_cr_approved_before_merge)
        except Exception:
            pass
        # Optional monkey patch (config: suppress_unmerged_after_approval)
        try:
            from django.conf import settings as dj_settings
            suppress = dj_settings.PLUGINS_CONFIG.get('netbox_branch_review', {}).get('suppress_unmerged_after_approval', False)
            if suppress:
                from netbox_branching.models.branches import Branch
                from .models import ChangeRequest, CRStatusChoices
                if hasattr(Branch, 'get_unmerged_changes') and not hasattr(Branch, '_nbcr_orig_get_unmerged_changes'):
                    Branch._nbcr_orig_get_unmerged_changes = Branch.get_unmerged_changes

                    def _patched_get_unmerged_changes(self, *args, **kwargs):
                        qs = ChangeRequest.objects.filter(branch_id=self.pk)
                        if qs.filter(status__in=[CRStatusChoices.APPROVED, CRStatusChoices.IMPLEMENTED]).exists():
                            try:
                                original = Branch._nbcr_orig_get_unmerged_changes(self, *args, **kwargs)
                            except Exception:
                                original = None
                            if original is not None and hasattr(original, 'none'):
                                return original.none()
                            class _Empty:
                                def count(self): return 0
                                def __iter__(self): return iter(())
                                def __len__(self): return 0
                            return _Empty()
                        return Branch._nbcr_orig_get_unmerged_changes(self, *args, **kwargs)
                    Branch.get_unmerged_changes = _patched_get_unmerged_changes
        except Exception:
            pass

config = BranchReviewConfig
