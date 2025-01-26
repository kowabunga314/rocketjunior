from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from entity.models import Attribute, Entity


class EntitySerializer(serializers.ModelSerializer):
    path = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = Entity
        fields = ['id', 'name', 'parent', 'path', 'tree_id', 'created_at', 'updated_at']

    def validate_name(self, value):
        if '/' in value:
            raise ValidationError('Entity names cannot contain \'/\' (forward slash).')
        return value
    
    def update(self, instance, validated_data):
        # Update the instance with the validated data
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Save the instance explicitly to trigger the post_save signal
        instance.save()

        return instance


class AttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attribute
        fields = ['id', 'entity', 'key', 'value', 'created_at', 'updated_at']


class GenericEASerializer(serializers.ModelSerializer):
    dynamic_dict = serializers.DictField(child=serializers.CharField(), required=False)

    class Meta:
        model = Entity
        fields = ['dynamic_dict']

    def to_internal_value(self, data):
        validated_data = super().to_internal_value(data)
        # Set up dynamic_dict object
        dynamic_fields = {k: v for k, v in data.items() if k not in self.fields}
        if dynamic_fields:
            validated_data['dynamic_dict'] = dynamic_fields
        return validated_data
    
    def create(self, validated_data):
        # Get dynamic_dict
        dynamic_dict = validated_data.get('dynamic_dict', {})
        if not dynamic_dict:
            # Create entity if no payload
            return self._handle_create_entity(self.context)
        # Create attribute if payload
        return self._handle_create_attribute(dynamic_dict, self.context)
    
    def _handle_create_entity(self, context):
        name = self.context.get('entity_name')
        parent = self.context.get('parent_entity')
        with transaction.atomic():
            entity = Entity.objects.create(parent=parent, name=name)
        return entity.subtree()
    
    def _handle_create_attribute(self, dynamic_dict, context):
        path = context.get('path')
        entity = Entity.objects.get(path=path)
        # Create attribute for each key/value pair provided
        with transaction.atomic():
            for key,value in dynamic_dict.items():
                Attribute.objects.create(
                    entity=entity,
                    key=key,
                    value=value
                )
        entity.refresh_from_db()
        return entity.subtree()
        