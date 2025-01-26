from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest import skip

from entity.models import Attribute, Entity


class EntityViewSetTestCase(APITestCase):
    def setUp(self):
        # Create test entities
        self.rocket = Entity.objects.create(name="Rocket")
        self.stage1 = Entity.objects.create(name="Stage1", parent=self.rocket)
        self.stage1engine1 = Entity.objects.create(name="Engine1", parent=self.stage1)
        self.stage1engine2 = Entity.objects.create(name="Engine2", parent=self.stage1)
        self.stage2 = Entity.objects.create(name="Stage2", parent=self.rocket)
        self.stage2engine1 = Entity.objects.create(name="Engine1", parent=self.stage2)

        # Set pathing expectations
        self.rocket_path = f'/{self.rocket.name}'
        self.stage1_path = f'/{self.rocket.name}/{self.stage1.name}'
        self.stage1engine1_path = f'/{self.rocket.name}/{self.stage1.name}/{self.stage1engine1.name}'
        self.stage1engine2_path = f'/{self.rocket.name}/{self.stage1.name}/{self.stage1engine2.name}'

        # Set up URLs
        self.list_url = reverse('entity-list')  # URL for the list view
        self.detail_url = reverse('entity-detail', args=[self.rocket.id])  # URL for the detail view
        self.subtree_url = reverse('entity-subtree', args=[self.rocket.id])  # URL for the subtree action

        # Set up user and authentication
        self.user = self._create_user()
        self.client.force_authenticate(user=self.user)

    def _create_user(self):
        from django.contrib.auth.models import User
        return User.objects.create_user(username="testuser", password="password")

    def test_entity_list(self):
        """Test that the list endpoint returns all entities."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get('results')), Entity.objects.count())

    def test_entity_detail(self):
        """Test that the detail endpoint returns the correct entity."""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.rocket.name)

    def test_entity_subtree(self):
        """Test that the subtree action returns the correct hierarchy."""
        response = self.client.get(self.subtree_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify the structure of the subtree
        expected_subtree = self.rocket.subtree()
        self.assertEqual(response.data, expected_subtree)

    def test_entity_subtree_paths(self):
        """Test that the subtree action returns the correct hierarchy."""
        response = self.client.get(self.subtree_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verify the root node path
        self.assertEqual(response.data.get('path'), self.rocket_path)

        s1e1_subtree_url = reverse('entity-subtree', args=[self.stage1engine1.id])
        response = self.client.get(s1e1_subtree_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verify the child node path
        self.assertEqual(response.data.get('path'), self.stage1engine1_path)

    def test_create_entity(self):
        """Test that we can create a new entity."""
        data = {
            "name": "Kickstage",
            "parent": self.rocket.id
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Entity.objects.filter(name="Kickstage").count(), 1)

    def test_update_entity(self):
        """Test that we can update an entity."""
        data = {
            "name": "Rocket2"
        }
        response = self.client.patch(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.rocket.refresh_from_db()
        self.assertEqual(self.rocket.name, "Rocket2")

    def test_delete_entity(self):
        """Test that we can delete an entity."""
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Entity.objects.filter(id=self.rocket.id).exists())

    def test_subtree_invalid_entity(self):
        """Test that the subtree action returns 404 for a nonexistent entity."""
        invalid_url = reverse('entity-subtree', args=[999])  # ID 999 does not exist
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class AttributeViewSetTestCase(APITestCase):
    def setUp(self):
        # Create test entities
        self.rocket = Entity.objects.create(name="Rocket")
        self.stage1 = Entity.objects.create(name="Stage1", parent=self.rocket)
        self.stage1engine1 = Entity.objects.create(name="Engine1", parent=self.stage1)
        self.stage1engine2 = Entity.objects.create(name="Engine2", parent=self.stage1)
        self.stage2 = Entity.objects.create(name="Stage2", parent=self.rocket)
        self.stage2engine1 = Entity.objects.create(name="Engine1", parent=self.stage2)

        # Create test attributes
        # Rocket
        Attribute.objects.create(
            entity=self.rocket,
            key='Height',
            value='18.000'
        )
        Attribute.objects.create(
            entity=self.rocket,
            key='Mass',
            value='12000.000'
        )
        # Stage1-Engine1
        self.s1e1_thrust = Attribute.objects.create(
            entity=self.stage1engine1,
            key='Thrust',
            value='9.493'
        )
        self.s1e1_isp = Attribute.objects.create(
            entity=self.stage1engine1,
            key='ISP',
            value='12.156'
        )
        # Stage1-Engine2
        Attribute.objects.create(
            entity=self.stage1engine2,
            key='Thrust',
            value='9.413'
        )
        Attribute.objects.create(
            entity=self.stage1engine2,
            key='ISP',
            value='11.632'
        )
        # Stage2-Engine1
        Attribute.objects.create(
            entity=self.stage2engine1,
            key='Thrust',
            value='1.622'
        )
        Attribute.objects.create(
            entity=self.stage2engine1,
            key='ISP',
            value='15.110'
        )

        # Set up URLs
        self.subtree_url = reverse('entity-subtree', args=[self.stage1engine1.id])  # URL for the subtree action

        # Set up user and authentication
        self.user = self._create_user()
        self.client.force_authenticate(user=self.user)

    def _create_user(self):
        from django.contrib.auth.models import User
        return User.objects.create_user(username="testuser", password="password")

    @skip
    def test_get_entity_with_attributes(self):
        """Test that the detail endpoint returns the correct entity attributes."""
        detail_url = reverse('entity-detail', args=[self.stage1engine1.id])
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('name'), self.stage1engine1.name)
        thrust_value = self.stage1engine1.attributes.filter(key='Thrust').first().value
        isp_value = self.stage1engine1.attributes.filter(key='ISP').first().value

        self.stage1engine1.refresh_from_db()
        self.assertEqual(self.stage1engine1.properties.get('Thrust'), thrust_value)
        self.assertEqual(self.stage1engine1.properties.get('ISP'), isp_value)

    def test_add_attribute_to_entity(self):
        """Test that we can add a new attribute to an entity."""
        data = {
            "entity": self.stage1engine1.id,
            "key": "Mass",
            "value": 1.450
        }
        attribute_url = reverse('attribute-list')
        response = self.client.post(attribute_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Attribute.objects.filter(
            entity=self.stage1engine1,
            key="Mass"
        ).count(), 1)

        # Check properties on subtree request
        response = self.client.get(self.subtree_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify the structure of the subtree
        self.stage1engine1.refresh_from_db()
        properties = response.data.get('properties')
        self.assertIsNotNone(properties)
        response_mass = properties.get('Mass')
        self.assertIsNotNone(response_mass)
        s1e1_mass = self.stage1engine1.attributes.filter(key="Mass").first().value
        self.assertEqual(response_mass, s1e1_mass)

    def test_edit_attribute(self):
        """Test that we can alter an existing attribute on an entity."""
        data = {
            "entity": self.stage1engine1.id,
            "key": "ISP",
            "value": "300"
        }
        attribute_url = reverse('attribute-detail', args=[self.s1e1_isp.id])
        response = self.client.put(attribute_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Attribute.objects.filter(
            entity=self.stage1engine1,
            key="ISP"
        ).count(), 1)

        # Check properties on subtree request
        response = self.client.get(self.subtree_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify the structure of the subtree
        self.stage1engine1.refresh_from_db()
        properties = response.data.get('properties')
        self.assertIsNotNone(properties)
        response_isp = properties.get('ISP')
        self.assertIsNotNone(response_isp)
        s1e1_isp = self.stage1engine1.attributes.filter(key="ISP").first().value
        self.assertEqual(response_isp, s1e1_isp)

    def test_delete_attribute(self):
        """Test that we can delete an existing attribute on an entity."""
        attribute_url = reverse('attribute-detail', args=[self.s1e1_isp.id])
        response = self.client.delete(attribute_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Attribute.objects.filter(
            entity=self.stage1engine1.id,
            key="ISP"
        ).count(), 0)

        # Check that object is removed from database
        s1e1_isp_queryset = Attribute.objects.filter(
            entity=self.stage1engine1,
            key='ISP'
        )
        self.assertEqual(s1e1_isp_queryset.count(), 0)

        # Check properties on subtree request
        response = self.client.get(self.subtree_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify the structure of the subtree
        self.stage1engine1.refresh_from_db()
        properties = response.data.get('properties')
        self.assertIsNotNone(properties)
        response_isp = properties.get('ISP')
        self.assertIsNone(response_isp)
        s1e1_isp_count = self.stage1engine1.attributes.filter(key="ISP").count()
        self.assertEqual(s1e1_isp_count, 0)
