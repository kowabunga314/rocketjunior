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
    
    def create(self, validated_data):
        # if 'path' not in validated_data:
        #     validated_data['path'] = ''
        print('Before super create in serializer')
        return super().create(validated_data)
    
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
