from django.dispatch import receiver
from extras.signals import post_object_diff

@receiver(post_object_diff)
def attach_diff_to_cr(sender, instance, diffs, request, **kwargs):
    return