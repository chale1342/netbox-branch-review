from .plugin import BranchReviewConfig  # noqa: F401

# Expose API URLs for NetBox to mount under /api/plugins/netbox-branch-review/
try:
    from .api import urls as api_urls  # noqa: F401
except Exception:
    api_urls = []