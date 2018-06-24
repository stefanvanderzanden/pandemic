from django.contrib import admin
from .models import InfectionCard


class InfectionCardAdmin(admin.ModelAdmin):
    list_display = ('city',)


admin.site.register(InfectionCard, InfectionCardAdmin)