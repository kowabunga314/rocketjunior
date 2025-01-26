from decimal import Decimal, ROUND_DOWN
from collections import defaultdict
from django.db import models, connection, transaction


class EntityManager(models.Manager):
    def update_child_paths(self, old_path, parent_path):
        """
        Updates the paths of all child entities based on the parent entity's path.

        Args:
            old_path (str): The path belonging to parent entity used to identify update candidates.
            parent_path (str): The new base path to be applied to children..
        """
        if not old_path:
            # Post-save signal will handle path
            return
        if not parent_path:
            raise ValueError("The parent entity must have a valid path.")

        # Fetch all children of the parent entity
        child_entities = self.filter(
            path__startswith=old_path
        ).exclude(path=old_path)

        # Prepare updates for bulk update
        updates = []
        for child in child_entities:
            # Compute the new path
            new_path = child.path.replace(old_path, parent_path)
            updates.append((child.id, new_path))

        # Perform the bulk update using raw SQL
        if updates:
            with connection.cursor() as cursor:  # Use the default database connection
                for child_id, new_path in updates:
                    cursor.execute(
                        """
                        UPDATE entity_entity
                        SET path = %s
                        WHERE id = %s
                        """,
                        [new_path, child_id],
                    )

    def update_child_paths_raw(self, old_path, parent_path):
        """
        Updates the paths of all child entities based on the parent entity's path.

        Args:
            old_path (str): The path belonging to parent entity used to identify update candidates.
            parent_path (str): The new base path to be applied to children..
        """
        if not old_path:
            # Post-save signal will handle path
            return
        if not parent_path:
            raise ValueError("The parent entity must have a valid path.")
        # Abort method if paths match
        if old_path == parent_path:
            return

        with connection.cursor() as cursor:
            query = """
                UPDATE entity_entity
                SET path = REPLACE(path, %s, %s)
            """
            cursor.execute(query, [old_path, parent_path])

    def update_child_trees(self, path, tree_id):
        if not path or not tree_id:
            raise ValueError('path and tree_id required.')

        with transaction.atomic():
            descendant_entities = self.select_for_update().filter(
                path__startswith=path
            ).exclude(path=path)

            # Prepare descendant for bulk update
            for descendant in descendant_entities:
                # Compute the new path
                descendant.tree_id = tree_id

            # Perform the bulk update
            self.bulk_update(descendant_entities, ['tree_id'])

    def path_exists(self, path):
        return [d.id for d in self.filter(path=path)]

    def fetch_descendants(self, root_path):
        with connection.cursor() as cursor:
            query = """
                SELECT e.id AS entity_id,
                    e.name AS entity_name,
                    e.path AS entity_path,
                    e.parent_id AS parent_id,
                    a.key AS attribute_key,
                    a.value AS attribute_value,
                    a.str_value AS attribute_quantizer
                FROM entity_entity e
                LEFT JOIN entity_attribute a ON e.id = a.entity_id
                WHERE e.path LIKE %s
                ORDER BY e.path
            """
            cursor.execute(query, [f"{root_path}%"])
            rows = cursor.fetchall()
        return rows

    def build_tree(self, root_path):
        rows = self.fetch_descendants(root_path)

        # Prepare entity and attribute receptacles
        entities = {}
        attributes = defaultdict(lambda: defaultdict(Decimal))  # Use Decimal for precision

        for row in rows:
            # Break up row into fields
            entity_id, name, path, parent_id, attr_key, attr_value, attr_quantizer = row
            # Ensure each entity is in the dictionary
            if entity_id not in entities:
                # Save entity using path as key
                entities[path] = {
                    "id": entity_id,
                    "name": name,
                    "path": path,
                    "properties": {},
                    "descendants": []
                }

            # Add attributes to the corresponding entity
            if attr_key:
                attributes[path][attr_key] = attr_value.quantize(
                    Decimal(attr_quantizer), rounding=ROUND_DOWN
                ) if attr_value and attr_quantizer else None

        # Merge attributes into entities
        for entity_path, props in attributes.items():
            if entity_path in entities:
                entities[entity_path]["properties"] = props

        # Construct the subtree
        tree = {}
        for entity in entities.values():
            if entity["path"] == root_path:
                # Handle root node
                tree = entity
            else:
                # Add to parent's descendants
                parent_path = "/".join(entity["path"].split("/")[:-1])
                # Look up parent by path
                parent = entities.get(parent_path)
                if parent:
                    parent["descendants"].append(entity)

        return tree
