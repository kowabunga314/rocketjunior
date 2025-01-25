from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.exceptions import ValidationError

from entity.models import Entity


# @receiver(post_save, sender=Entity)
# def set_path(sender, instance, created, **kwargs):
#     '''
#     Signal used to generate entity path immediately after creation.

#     This signal is needed because entity paths use object IDs, which are not
#     available until an object has been saved for the first time.
#     '''
#     # Block signals in process
#     if not created or getattr(instance, '_locked', False):
#         return
#     instance._locked = True

#     # Update path of current entity
#     try:
#         if instance.parent is not None and f'/{instance.id}/' in instance.parent.path:
#             raise ValidationError('A node cannot be a descendant of itself.')
#         if created and not instance.path:
#             instance.path = instance._generate_path()
#         instance.save(update_fields=['path'])
#     finally:
#         instance._locked = False


@receiver(post_save, sender=Entity)
def set_tree_id(sender, instance, created, **kwargs):
    # Block signals in process
    if not created or getattr(instance, '_locked', False):
        return
    instance._locked = True

    # Update tree ID
    try:
        if instance.parent is not None:
            instance.tree_id = instance.parent.tree_id
        else:
            instance.tree_id = instance.id
        instance.save()
    finally:
        instance._locked = False

