from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from entity.models import Entity

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
        self.rocket_path = f'/{self.rocket.id}/'
        self.stage1_path = f'/{self.rocket.id}/{self.stage1.id}/'
        self.stage1engine1_path = f'/{self.rocket.id}/{self.stage1.id}/{self.stage1engine1.id}/'
        self.stage1engine2_path = f'/{self.rocket.id}/{self.stage1.id}/{self.stage1engine2.id}/'

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
