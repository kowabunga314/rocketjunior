from decouple import config
from django.db import models, transaction
from rest_framework.exceptions import ValidationError


class Entity(models.Model):
    name = models.CharField(max_length=256, null=False, blank=False)
    parent = models.ForeignKey(to='self', null=True, blank=True, on_delete=models.SET_NULL, related_name='descendants')
    path = models.CharField(max_length=2048, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def subtree(self):
        data = self._repr(root=True)
        return data

    def _generate_path(self):
        # Base case
        if self.parent == None:
            return f'/{self.id}/'
        # Prevent cyclic references
        if f'/{self.id}/' in self.parent.path:
            raise ValidationError('A node cannot be a descendant of itself.')
        
        return f'{self.parent.path}{self.id}/'
    
    def update_path(self):
        with transaction.atomic():
            # Call self.save to generate path automatically
            self.save()
            for child in self.descendants.all():
                child.update_path()
    
    def _repr(self, root=False):
        data = {}
        data['name'] = self.name
        if root:
            data['path'] = self.path
            data['parent'] = self.parent.name if self.parent is not None else None
        data['properties'] = self._get_attributes()
        data['descendants'] = [x._repr() for x in self.descendants.all()]

        return data

    def _get_attributes(self):
        return [a.as_dict() for a in self.attributes.all()]





# TODO: Consider making type-specific attributes like IntegerAttribute, DecimalAttribute, or BooleanAttribute
class Attribute(models.Model):
    class DataTypeChoices(models.TextChoices):
        STR = 'str', 'String'
        INT = 'int', 'Integer'
        FLT = 'flt', 'Float'

    entity = models.ForeignKey(to=Entity, null=False, blank=False, on_delete=models.CASCADE, related_name='attributes')
    key = models.CharField(max_length=256, null=True, blank=True)
    value = models.CharField(max_length=256, null=True, blank=True)
    data_type = models.CharField(max_length=3, choices=DataTypeChoices.choices, default=DataTypeChoices.STR)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_value(self):
        if self.data_type == self.DataTypeChoices.INT:
            return int(self.value)
        if self.data_type == self.DataTypeChoices.FLT:
            return float(self.value)
        else:
            return self.value
    
    def as_dict(self):
        return {self.key: self.get_value()}
