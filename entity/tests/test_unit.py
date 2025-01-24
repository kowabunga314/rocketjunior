from django.test import TestCase
from rest_framework.exceptions import ValidationError

from entity.models import Attribute, Entity

class EntityUnitTestCase(TestCase):
    def test_entity_creation(self):
        name = "Test Entity"
        entity = Entity.objects.create(
            parent=None,
            name=name
        )
        self.assertEqual(entity.name, name)
        self.assertIsNotNone(entity.path)
        self.assertEqual(entity.path, f'/{entity.id}/')
        self.assertIsNone(entity.parent)
    
    def test_entity_parent_relationship(self):
        parent_name = "Parent Entity"
        child_name = "Child Entity"

        parent = Entity.objects.create(name=parent_name)
        child = Entity.objects.create(name=child_name, parent=parent)

        self.assertEqual(child.name, child_name)
        self.assertIsNotNone(child.path)
        self.assertEqual(child.path, f'/{parent.id}/{child.id}/')
        self.assertEqual(child.path, f'{parent.path}{child.id}/')
        self.assertIsNotNone(child.parent)
        self.assertEqual(child.parent.id, parent.id)

    def test_cyclic_relationship_forbidden(self):
        parent_name = "Parent Entity"
        child_name = "Child Entity"

        parent = Entity.objects.create(name=parent_name)
        child = Entity.objects.create(name=child_name, parent=parent)

        parent.parent = child
        with self.assertRaises(ValidationError):
            parent.save()
    
    def test_entity_delete_set_null(self):
        parent_name = "Parent Entity"
        child_name = "Child Entity"

        parent = Entity.objects.create(name=parent_name)
        child = Entity.objects.create(name=child_name, parent=parent)

        parent.delete()
        child.refresh_from_db()

        self.assertIsNone(child.parent)


class AttributeUnitTestCase(TestCase):
    def test_attribute_creation(self):
        entity_name = "Test Entity"
        entity = Entity.objects.create(name=entity_name)

        key = 'Weight'
        value = 12.0
        attribute = Attribute.objects.create(
            entity=entity,
            key=key,
            value=value,
            data_type=Attribute.DataTypeChoices.FLT
        )

        self.assertIsNotNone(attribute.entity)
        self.assertEqual(attribute.entity.id, entity.id)
        self.assertEqual(attribute.key, key)
        self.assertEqual(attribute.value, value)

    def test_entity_delete_cascade(self):
        entity_name = "Test Entity"
        entity = Entity.objects.create(name=entity_name)
        entity_id = entity.id

        key = 'Weight'
        value = 12.0
        attribute = Attribute.objects.create(
            entity=entity,
            key=key,
            value=value,
            data_type=Attribute.DataTypeChoices.FLT
        )
        attribute_id = attribute.id
        
        self.assertIsNotNone(attribute.entity)
        self.assertEqual(attribute.entity.id, entity.id)
        
        entity.delete()

        self.assertEqual(
            Entity.objects.filter(id=entity_id).count(),
            0
        )

        self.assertEqual(
            Attribute.objects.filter(id=attribute_id).count(),
            0
        )

