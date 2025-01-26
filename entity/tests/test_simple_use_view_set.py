from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from entity.models import Entity, Attribute


class SimpleUseViewSetTestCase(APITestCase):
    def setUp(self):
        # Create some initial entities
        self.rocket = Entity.objects.create(name='Rocket', parent=None)
        self.stage1 = Entity.objects.create(name='Stage1', parent=self.rocket)
        self.engine1 = Entity.objects.create(name='Engine1', parent=self.stage1)

    def test_get_entity_subtree(self):
        # Create a few more entities
        engine2 = Entity.objects.create(name='Engine2', parent=self.stage1)
        engine3 = Entity.objects.create(name='Engine3', parent=self.stage1)
        turbopump1 = Entity.objects.create(name='Turbopump1', parent=self.engine1)
        # Create a few attributes
        thrust = 9.493
        isp = 12.156
        mass = 175.000
        Attribute.objects.create(entity=self.engine1, key='Thrust', value=thrust)
        Attribute.objects.create(entity=self.engine1, key='ISP', value=isp)
        Attribute.objects.create(entity=turbopump1, key='Mass', value=mass)
        # Refresh entities with attributes
        self.engine1.refresh_from_db()
        turbopump1.refresh_from_db()
        # Test GET request for an existing entity
        url = reverse('simple-use-api', kwargs={'path': 'Rocket/Stage1'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verify that the subtree contains the child entity in the expected location
        descendants = response.data.get('descendants')
        descendant_names = [d.get('name') for d in descendants]
        self.assertIn(self.engine1.name, descendant_names)
        self.assertIn(engine2.name, descendant_names)
        self.assertIn(engine3.name, descendant_names)
        # Verify that Engine1 attributes are formed correctly
        engine1_data = [d for d in descendants if d.get('name') == self.engine1.name][0]
        self.assertIn('Thrust', engine1_data.get('properties').keys())
        self.assertIn('ISP', engine1_data.get('properties').keys())
        self.assertEqual(engine1_data.get('properties').get('Thrust'), thrust)
        self.assertEqual(engine1_data.get('properties').get('ISP'), isp)
        # Get Turbopump1 data from Engine1
        self.assertIn(turbopump1.name, [d.get('name') for d in engine1_data.get('descendants')])
        turbopump1_data = engine1_data.get('descendants')[0]
        # Verify Turbopump1 path
        self.assertEqual(turbopump1_data.get('path'), turbopump1.path)
        # Verify Turbopump1 attributes
        self.assertIn('Mass', turbopump1_data.get('properties').keys())
        self.assertEqual(turbopump1_data.get('properties').get('Mass'), mass)
        # Create an unrelated entity
        Entity.objects.create(name='Rocket2', parent=None)
        # Get unrelated entity's subtree
        url = reverse('simple-use-api', kwargs={'path': 'Rocket2'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verify that the subtree contains the child entity in the expected location
        descendants = response.data.get('descendants')
        self.assertEqual(len(descendants), 0)

    def test_get_entity_not_found(self):
        # Test GET request for a non-existent entity
        url = reverse('simple-use-api', kwargs={'path': 'Stage2'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # Method returns a 200 OK with a message
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'Entity not found.')

    def test_create_new_root_entity(self):
        # Test creating a new entity under an existing parent
        url = reverse('simple-use-api', kwargs={'path': 'Rocket2'})
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify the new entity was created
        new_entity = Entity.objects.filter(name='Rocket2', path='/Rocket2').first()
        self.assertIsNotNone(new_entity)
        self.assertIsNone(new_entity.parent)

    def test_create_new_child_entity(self):
        # Test creating a new entity under an existing parent
        url = reverse('simple-use-api', kwargs={'path': 'Rocket/Stage2'})
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify the new entity was created
        new_entity = Entity.objects.filter(name='Stage2', path='/Rocket/Stage2').first()
        self.assertIsNotNone(new_entity)
        self.assertEqual(new_entity.parent, self.rocket)

    def test_add_attribute_to_entity(self):
        # Test creating attributes for an existing entity
        url = reverse('simple-use-api', kwargs={'path': 'Rocket/Stage1/Engine1'})
        thrust = '9.493'
        isp = '12.156'
        payload = {
            'Thrust': thrust,
            'ISP': isp
        }
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify the attributes were created
        attributes = Attribute.objects.filter(entity=self.engine1)
        self.assertEqual(attributes.count(), 2)
        self.assertTrue(attributes.filter(key='Thrust', value=thrust).exists())
        self.assertTrue(attributes.filter(key='ISP', value=isp).exists())

    def test_create_entity_under_nonexistent_parent(self):
        # Test creating an entity under a non-existent parent
        url = reverse('simple-use-api', kwargs={'path': 'NonExistentParent/ChildEntity'})
        response = self.client.post(url, {}, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Verify no entity was created
        self.assertFalse(Entity.objects.filter(name='ChildEntity').exists())

    def test_invalid_payload_for_attribute_creation(self):
        # Test invalid payload when creating attributes
        url = reverse('simple-use-api', kwargs={'path': 'Rocket/Stage1'})
        payload = 'invalid value'
        response = self.client.post(url, payload, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Verify no attributes were created
        self.assertFalse(Attribute.objects.filter(entity=self.stage1).exists())
