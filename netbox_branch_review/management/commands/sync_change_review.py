from django.core.management.base import BaseCommand
from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

APP = 'netbox_branch_review'

class Command(BaseCommand):
    help = 'Sync Change Request permissions and default groups (Change Managers / Change Reviewers).'

    def add_arguments(self, parser):
        parser.add_argument('--no-peer-group', action='store_true', help='Skip creating the peer review group')
        parser.add_argument('--managers', default='Change Managers', help='Name for the managers group')
        parser.add_argument('--reviewers', default='Change Reviewers', help='Name for the peer reviewers group')

    def handle(self, *args, **opts):
        ChangeRequest = apps.get_model(APP, 'ChangeRequest')
        ct = ContentType.objects.get_for_model(ChangeRequest)

        perms_wanted = [
            ('approve_changerequest', 'Can approve change request'),
            ('merge_changerequest', 'Can merge branch for change request'),
            ('peer_review_changerequest', 'Can peer review change request'),
        ]
        created = 0
        for codename, name in perms_wanted:
            _, was_created = Permission.objects.update_or_create(
                codename=codename,
                content_type=ct,
                defaults={'name': name},
            )
            if was_created:
                created += 1
        self.stdout.write(self.style.SUCCESS(f'Permissions ensured (new: {created}).'))

        mgr_group, _ = Group.objects.get_or_create(name=opts['managers'])
        mgr_perms = Permission.objects.filter(content_type=ct, codename__in=[p[0] for p in perms_wanted])
        mgr_group.permissions.add(*mgr_perms)
        self.stdout.write(self.style.SUCCESS(f'Manager group "{mgr_group.name}" synced.'))

        if not opts['no_peer_group']:
            peer_group, _ = Group.objects.get_or_create(name=opts['reviewers'])
            peer_perm = Permission.objects.get(content_type=ct, codename='peer_review_changerequest')
            peer_group.permissions.add(peer_perm)
            self.stdout.write(self.style.SUCCESS(f'Peer review group "{peer_group.name}" synced.'))
        else:
            self.stdout.write('Peer group skipped.')

        self.stdout.write(self.style.SUCCESS('Sync complete.'))
