from decimal import Decimal, ROUND_DOWN
from django.db import models
from rest_framework.exceptions import ValidationError

from entity.managers import EntityManager


class Entity(models.Model):
    name = models.CharField(max_length=256, null=False, blank=False, db_index=True)
    parent = models.ForeignKey(to='self', null=True, blank=True, on_delete=models.SET_NULL, related_name='descendants')
    path = models.CharField(max_length=2048, null=True, blank=True, db_index=True)
    tree_id = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = EntityManager()

    class Meta:
        ordering = ['path']
        constraints = [
            models.UniqueConstraint(
                fields=['parent', 'path'],
                condition=models.Q(parent__isnull=False, path__isnull=False),
                name='unique_parent_path'
            )
        ]

    def save(self, *args, **kwargs):
        # Handle entity path
        old_path = self.path
        self.path = self._generate_name_path()
        # Check for duplicate paths
        extant = Entity.objects.path_exists(self.path)
        if extant:
            if len(extant) > 1 or self.id is None or (self.id is not None and self.id not in extant):
                raise ValidationError({
                    'ValidationError': {
                        'message': f'Entity path is not unique: {self.path}',
                        'hint': 'If this is a root node, its name must be unique among root nodes. If this is a '
                                'descendant node, its name must be unique among its siblings'
                    }
                })
        # Update child paths
        Entity.objects.update_child_paths_raw(old_path, self.path)

        # Save the object
        super().save(*args, **kwargs)

    def subtree(self):
        return Entity.objects.build_tree(self.path)

    def _generate_name_path(self):
        # Base case
        if self.parent is None:
            return f'/{self.name}'
        # Return parent path with self.name appended
        return f'{self.parent.path}/{self.name}'

    def _repr(self, root=False):
        data = {}
        data['id'] = self.id
        data['name'] = self.name
        data['path'] = self.path
        if root:
            data['parent'] = self.parent.name if self.parent is not None else None
        data['properties'] = self.get_attributes()
        data['descendants'] = [x._repr() for x in self.descendants.prefetch_related('descendants')]

        return data

    def __str__(self):
        return f'{self.name}: {self.path}'

    def get_attributes(self):
        return {a.key: a.get_value() for a in self.attributes.all()}


class Attribute(models.Model):
    entity = models.ForeignKey(to=Entity, null=False, blank=False, on_delete=models.CASCADE, related_name='attributes')
    key = models.CharField(max_length=256, null=True, blank=True)
    value = models.DecimalField(max_digits=20, decimal_places=10, null=True, blank=True)
    str_value = models.CharField(max_length=31)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']
        constraints = [
            models.UniqueConstraint(
                fields=['entity', 'key'],
                condition=models.Q(entity__isnull=False, key__isnull=False),
                name='unique_entity_key'
            )
        ]

    def save(self, *args, **kwargs):
        self.str_value = str(self.value)

        # Save the object
        super().save(*args, **kwargs)

    def get_value(self):
        return self.value.quantize(Decimal(self.str_value), rounding=ROUND_DOWN)

    def as_dict(self):
        return {self.key: self.get_value()}

    def __str__(self):
        return f'({self.key}: {self.value})'
