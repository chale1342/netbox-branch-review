from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_migrate
from django.dispatch import receiver

APP_NAME = "netbox_branch_review"


@receiver(post_migrate)
def ensure_perms_and_group(app_config, **kwargs):
    # Only act for our app
    if getattr(app_config, "name", "") != APP_NAME:
        return

    try:
        ChangeRequest = apps.get_model(APP_NAME, "ChangeRequest")
    except Exception:
        # Model not ready; nothing to do
        return

    ct = ContentType.objects.get_for_model(ChangeRequest)
    wanted = [
        ("approve_changerequest", "Can approve change request"),
        ("merge_changerequest", "Can merge branch for change request"),
        ("peer_review_changerequest", "Can peer review change request"),
        ("revoke_changerequest", "Can revoke approvals on change request"),
    ]

    # Create/ensure permissions
    for codename, name in wanted:
        Permission.objects.update_or_create(
            codename=codename,
            content_type=ct,
            defaults={"name": name},
        )

    # Optionally create/maintain default groups with appropriate perms
    cfg = settings.PLUGINS_CONFIG.get(APP_NAME, {})
    if cfg.get("auto_create_group", True):
        group_name = cfg.get("auto_group_name", "Change Managers")
        g, _ = Group.objects.get_or_create(name=group_name)
        perms = Permission.objects.filter(
            content_type=ct, codename__in=[c for c, _ in wanted]
        )
        g.permissions.add(*perms)

        # Peer reviewers group (only peer review permission)
        peer_group_name = cfg.get("auto_peer_group_name")
        if peer_group_name:
            pg, _ = Group.objects.get_or_create(name=peer_group_name)
            try:
                peer_perm = Permission.objects.get(
                    content_type=ct, codename="peer_review_changerequest"
                )
                pg.permissions.add(peer_perm)
            except Permission.DoesNotExist:
                pass
