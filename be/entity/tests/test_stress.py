import time
from django.db import connection
from django.urls import reverse
from pathlib import Path
from rest_framework.test import APITestCase


class LargeDatasetTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up file access
        FILENAME = 'test_data.sql'
        ROOT_DIR = Path(__file__).parent
        SQL_FILE = ROOT_DIR / FILENAME
        # Load the SQL dump into the test database
        with connection.cursor() as cursor:
            with open(SQL_FILE, 'r') as sql_file:
                cursor.execute(sql_file.read())

    def test_tree_performance(self):
        """Tests subtree performance on tree with over 40,000 nodes"""
        # Set up request
        root_path = '/Node.1.0'
        url = reverse('simple-use-api', kwargs={'path': root_path})
        # Time the operation
        start_time = time.time()
        response = self.client.get(url)
        # tree = root_entity.fetch_descendants()
        end_time = time.time()

        # Assert tree structure and performance
        tree = response.data
        self.assertEqual(tree["name"], "Node.1.0")
        self.assertTrue(len(tree["descendants"]) > 0)
        self.assertLess(end_time - start_time, 1, "Performance test exceeded 1 second")
