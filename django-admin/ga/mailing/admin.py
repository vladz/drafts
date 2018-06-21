from django.contrib import admin

from mailing.models import Template

@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ('name', )
    readonly_fields = ('slug', )

    def has_add_permission(self, request):
        return False
