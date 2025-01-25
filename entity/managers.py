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
