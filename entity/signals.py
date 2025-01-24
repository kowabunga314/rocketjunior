from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.exceptions import ValidationError

from entity.models import Entity


@receiver(post_save, sender=Entity)
def set_path(sender, instance, created, **kwargs):
    if getattr(instance, '_locked', False):
        # Block signals in process
        return
    instance._locked = True

    if instance.parent is not None and f'/{instance.id}/' in instance.parent.path:
        raise ValidationError('A node cannot be a descendant of itself.')
    if created and not instance.path:
        instance.path = instance._generate_path()
    instance.save(update_fields=['path'])

    instance._locked = False
