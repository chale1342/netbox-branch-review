from extras.plugins import PluginConfig

class BranchReviewConfig(PluginConfig):
    name = "netbox_branch_review"
    verbose_name = "Branch Review"
    description = "Require approval before merging branches"
    version = "0.1.0"
    author = "Sunwire NOC"
    author_email = "noc@sunwire.ca"
    base_url = "branch-review"
    min_version = "4.0.0"
    max_version = "4.999"
    required_settings = []
    default_settings = {
        "require_two_approvals": True,
        "enforce_branching": True,
    }

    def ready(self):
        try:
            from netbox_branching.validators import register_pre_action_validator
            from .validators import require_cr_approved_before_merge
            register_pre_action_validator(require_cr_approved_before_merge)
        except Exception:
            pass

config = BranchReviewConfig
