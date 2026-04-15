\# cotonourow/db_router.py

class PrefixRouter:
    """
    Routes database operations for the 'contacts' app
    based on a prefix hint (e.g., contacts_070, contacts_080, etc.).
    """

    def db_for_read(self, model, **hints):
        """Route read operations for 'Contact' model."""
        if model._meta.app_label == "contacts":
            prefix = hints.get("prefix")
            if prefix:
                return f"contacts_{prefix}"
        return "default"

    def db_for_write(self, model, **hints):
        """Route write operations for 'Contact' model."""
        if model._meta.app_label == "contacts":
            prefix = hints.get("prefix")
            if prefix:
                return f"contacts_{prefix}"
        return "default"

    def allow_relation(self, obj1, obj2, **hints):
        """Allow relations between objects in the same app."""
        if obj1._meta.app_label == "contacts" and obj2._meta.app_label == "contacts":
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Allow migrations:
        - Default DB: everything (admin, auth, sessions, etc.)
        - Contacts DBs: only models in 'contacts' app
        """
        if db == "default":
            return True

        if db.startswith("contacts_") and app_label == "contacts":
            return True

        # Block everything else
        return False