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
    
    # def create(self, validated_data):
    #     # if 'path' not in validated_data:
    #     #     validated_data['path'] = ''
    #     print('Before super create in serializer')
    #     return super().create(validated_data)
    
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
        fields = ['id', 'entity', 'key', 'value', 'data_type', 'created_at', 'updated_at']


class DynamicDictField(serializers.JSONField):
    def __init__(self, *args, **kwargs):
        kwargs['required'] = False
        kwargs['default'] = {}
        super().__init__(*args, **kwargs)

    def to_internal_value(self, data):
        if not isinstance(data, dict):
            raise serializers.ValidationError('Invalid input: expected dictionary')
        return super().to_internal_value(data)

class GenericEASerializer(serializers.ModelSerializer):
    dynamic_dict = serializers.DictField(child=serializers.CharField(), required=False)

    class Meta:
        model = Entity
        fields = ['dynamic_dict']

    def to_internal_value(self, data):
        validated_data = super().to_internal_value(data)
        dynamic_fields = {k: v for k, v in data.items() if k not in self.fields}
        if dynamic_fields:
            validated_data['dynamic_dict'] = dynamic_fields
        return validated_data
    
    def create(self, validated_data):
        dynamic_dict = validated_data.get('dynamic_dict', {})

        if not dynamic_dict:
            name = self.context.get('entity_name')
            parent = self.context.get('parent_entity')
            entity = Entity.objects.create(parent=parent, name=name)
            return entity.subtree()
    
        path = self.context.get('path')
        entity = Entity.objects.get(path=path)
        with transaction.atomic():
            for key,value in dynamic_dict.items():
                Attribute.objects.create(
                    entity=entity,
                    key=key,
                    value=value
                )
        
        entity.refresh_from_db()
        print('\nentity.subtree(): ', entity.subtree())
        return entity.subtree()
        