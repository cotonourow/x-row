# cotonourow/db_router.py - UPGRADED VERSION

class PrefixRouter:
    def db_for_read(self, model, **hints):
        # Check if .using() was called with database alias
        if 'database' in hints:
            return hints['database']
        
        # Default for Contact model
        if model._meta.app_label == 'contacts':
            return 'contacts_070'
        return 'default'
    
    def db_for_write(self, model, **hints):
        if 'database' in hints:
            return hints['database']
        
        if model._meta.app_label == 'contacts':
            return 'contacts_070'
        return 'default'
    
    def allow_relation(self, obj1, obj2, **hints):
        return True
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if db == 'default':
            return True
        if db.startswith('contacts_'):
            return app_label == 'contacts'
        return False