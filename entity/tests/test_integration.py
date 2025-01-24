from rest_framework.test import APITestCase
from rest_framework import status
from entity.models import Attribute, Entity

class EntityAPITestCase(APITestCase):
    def setUp(self):
        """Set up initial data for the test"""
        self.entity_data = {
            'name': 'Test Entity',
            'description': 'This is a test entity'
        }
        self.entity = Entity.objects.create(**self.entity_data)
        self.url = '/api/entities/'

    def test_get_entities(self):
        """Test that we can get the list of entities"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)  # Check if there are any entities in the response

    def test_post_entity(self):
        """Test creating a new entity"""
        new_entity_data = {
            'name': 'New Entity',
            'description': 'A newly created entity'
        }
        response = self.client.post(self.url, new_entity_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], new_entity_data['name'])
        self.assertEqual(response.data['description'], new_entity_data['description'])

    def test_get_single_entity(self):
        """Test retrieving a single entity"""
        response = self.client.get(f'{self.url}{self.entity.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.entity.name)
        self.assertEqual(response.data['description'], self.entity.description)

    def test_delete_entity(self):
        """Test deleting an entity"""
        response = self.client.delete(f'{self.url}{self.entity.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # Verify it no longer exists
        response = self.client.get(f'{self.url}{self.entity.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def _create_entities(self):
        self.rocket = Entity.objects.create(
            name="Rocket",
            parent=None
        )
        self._create_root_attributes(self.root)
        self._create_first_stage(self.rocket)
        self._create_second_stage(self.rocket)

    def _create_root_attributes(self, entity):
        height = Attribute.objects.create(
            entity=entity,
            key='Height',
            value='18.000',
            data_type=Attribute.DataTypeChoices.FLT
        )
        weight = Attribute.objects.create(
            entity=entity,
            key='Weight',
            value='12000.000',
            data_type=Attribute.DataTypeChoices.FLT
        )

    def _create_first_stage(self, root):
        first_stage = Entity.objects.create(
            parent=root,
            name='Stage1'
        )
        first_stage.save()
        
        thrust = ['9.493', '9.413', '9.899']
        isp = ['12.156', '11.632', '12.551']
        for i in range(3):
            engine = Entity.objects.create(
                parent=first_stage,
                name=f'Engine{i}'
            )
            engine_thrust = Attribute.objects.create(
                entity=engine,
                key='Thrust',
                value=thrust[i]
            )
            engine_isp = Attribute.objects.create(
                entity=engine,
                key='ISP',
                value=isp[i]
            )
    
    def _create_second_stage(self, root):
        second_stage = Entity.objects.create(
            parent=root,
            name='Stage1'
        )
        second_stage.save()
        
        engine = Entity.objects.create(
            parent=second_stage,
            name=f'Engine1'
        )
        engine_thrust = Attribute.objects.create(
            entity=engine,
            key='Thrust',
            value='1.622'
        )
        engine_isp = Attribute.objects.create(
            entity=engine,
            key='ISP',
            value='15.110'
        )
