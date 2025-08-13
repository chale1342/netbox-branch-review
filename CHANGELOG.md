## Changelog

All notable changes to this project will be documented here. The format loosely follows Keep a Changelog and semantic versioning (pre-1.0: minor bumps may include breaking changes).

### [0.1.9] - 2025-08-13
Fixed
- Corrected indentation error in `BranchReviewConfig` (version attribute) that caused `IndentationError` on plugin import for 0.1.8 installs.
- General formatting and consistency cleanups across multiple source files (PEP8 / alignment).

### [0.1.8] - 2025-08-12
Fixed
- Added explicit plugin metadata (author, URL, license, description, min/max version) so details display in NetBox Plugins UI.
- Synchronized README project layout with current file set (removed non-existent plugin.py, listed migrations 0001-0004).

### [0.1.7] - 2025-08-12
Initial public release.
Added
- ChangeRequest model & approval workflow (single / dual approvals, optional self full approval).
- ChangeRequestAudit trail (approvals, revokes, peer reviews, merges, blocked attempts).
- Merge gate validator integrating with netbox-branching (optional; degrades gracefully if absent).
- Peer review action (non-status audit event).
- Revoke approvals action resetting status to pending (pre-implementation).
- Optional branch unmerged changes summary on detail page.
- API serializer & viewset for ChangeRequest.
- Packaging metadata (pyproject.toml) & wheel/sdist publication setup.
Changed
- Based model on PrimaryModel instead of NetBoxModel to suppress automatic changelog/journal integration.
Removed / Suppressed
- Changelog & journal tabs (stub routes + template override).
Fixed
- Previous reverse URL errors for missing changelog/journal views via placeholder views.
- Migration divergence with merge migration; added description & comments fields.
