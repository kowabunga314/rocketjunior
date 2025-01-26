from django.db.models.signals import post_save
from django.dispatch import receiver

from entity.models import Entity


@receiver(post_save, sender=Entity)
def set_tree_id(sender, instance, created, **kwargs):
    # Block signals in process
    if getattr(instance, '_locked', False):
        return
    instance._locked = True

    # Update tree ID
    try:
        if instance.parent is not None:
            instance.tree_id = instance.parent.tree_id
        else:
            instance.tree_id = instance.id
        instance.save()
        Entity.objects.update_child_trees(instance.path, instance.tree_id)
    finally:
        instance._locked = False
