from django.contrib import admin
from django.contrib.admin import register

from apps.game_tracker.models import Card, City, Affiliation, Region


@register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ('city', 'card_type', 'get_region')

    def get_region(self, obj):
        return obj.city.region
    get_region.short_description = 'Region'
    get_region.admin_order_field = 'city__region'


@register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'region', 'affiliation', 'has_safe_house', 'surveillance_level')
    list_filter = ('region', 'affiliation', 'has_safe_house', 'surveillance_level')


@register(Affiliation)
class AffiliationAdmin(admin.ModelAdmin):
    list_display = ('name',)


@register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')

