class LocationRouter:
    """
    A router to control all database operations on models in the
    route_app_labels applications.
    """

    route_app_labels = {"locations", }

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return "location"
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return "location"
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in self.route_app_labels:
            return db == "location"
        return None


class CreditRouter:
    route_app_labels = {"credits", }

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return "credits"
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return "credits"
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in self.route_app_labels:
            return db == "credits"
        return None
