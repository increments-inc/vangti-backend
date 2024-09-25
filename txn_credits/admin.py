from django.contrib import admin
from django.apps import apps


class MultiDBModelCreditsAdmin(admin.ModelAdmin):
    using = "credits"

    def save_model(self, request, obj, form, change):
        obj.save(using=self.using)

    def delete_model(self, request, obj):
        obj.delete(using=self.using)

    def get_queryset(self, request):
        return super().get_queryset(request).using(self.using)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        return super().formfield_for_foreignkey(
            db_field, request, using=self.using, **kwargs
        )

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        return super().formfield_for_manytomany(
            db_field, request, using=self.using, **kwargs
        )


class ListAdminCreditMixin(MultiDBModelCreditsAdmin):
    def __init__(self, model, admin_site):
        self.list_display = [
            field.name for field in model._meta.fields if field.name not in ["slug", "password"]
        ]
        self.readonly_fields = [
            field.name
            for field in model._meta.fields
            if field.name in ["slug", "id", "password", "user", "user_uid"]
        ]
        super().__init__(model, admin_site)


def register_models(*, app_name: str):
    app_models = apps.get_app_config(app_name).get_models()

    # Register models using the mixin
    for model in app_models:
        admin_class = type(f"{model.__name__}Admin", (ListAdminCreditMixin,), {})
        try:
            admin.site.register(model, admin_class)
        except admin.sites.AlreadyRegistered:
            pass


# register
register_models(app_name="txn_credits")
