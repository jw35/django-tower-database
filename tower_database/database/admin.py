from django.contrib import admin

# Register your models here.

from .models import Contact, Tower, ContactMap, Website

admin.site.site_header = "Ely DA Tower Database"
admin.site.site_title = "Database admin"
admin.site.index_title = "Database admin"


class ContactInline(admin.TabularInline):
	model = Tower.other_contacts.through
	verbose_name = "other contact"
	extra = 0

class PrimaryContactInline(admin.TabularInline):
	model = Tower
	fields = ["__str__"]
	readonly_fields = ["__str__"]
	verbose_name = "primary contact"
	extra = 0
	can_delete = False

class TowerInline(admin.TabularInline):
	model = Tower.other_contacts.through
	fields = ["role", "tower", "publish"]
	readonly_fields = ["role", "tower", "publish"]
	verbose_name = "as other contact"
	extra = 0
	can_delete = False

class WebsiteInline(admin.TabularInline):
	model = Website
	extra = 0

class ContactAdmin(admin.ModelAdmin):
	inlines= [PrimaryContactInline, TowerInline]
	search_fields = ["name", "email"]
	search_help_text = "Search by name or email"

class TowerAdmin(admin.ModelAdmin):
	inlines = [WebsiteInline, ContactInline]
	list_display = ["place", "dedication", "district", "bells"]
	list_filter = ["district", "report", "bells", "ringing", "ring_type", "day"]
	search_fields = ["place", "dedication", "full_dedication", "nickname"]
	search_help_text = "Search by place or dedication"

admin.site.register(Contact, ContactAdmin)
admin.site.register(Tower, TowerAdmin)
admin.site.register(Website)

