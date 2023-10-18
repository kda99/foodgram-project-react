from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from recipes.models import Ingredient


@admin.register(Ingredient)
class IngredientsAdmin(ImportExportModelAdmin):
    pass


admin.site.register(Ingredient, IngredientsAdmin)