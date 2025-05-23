from django.contrib import admin
from django.apps import apps
from import_export.admin import ExportActionMixin


class ListAdminMixin(ExportActionMixin, admin.ModelAdmin):
    def __init__(self, model, admin_site):
        self.list_display = [
            field.name for field in model._meta.fields if field.name not in ["slug" , "password"]
        ]
        self.readonly_fields = [
            field.name
            for field in model._meta.fields
            if field.name in ["slug", "id", "password"]
        ]
        super().__init__(model, admin_site)


def register_models(*, app_name: str):
    app_models = apps.get_app_config(app_name).get_models()

    # Register models using the mixin
    for model in app_models:
        admin_class = type(f"{model.__name__}Admin", (ListAdminMixin,), {})
        try:
            admin.site.register(model, admin_class)
        except admin.sites.AlreadyRegistered:
            pass
