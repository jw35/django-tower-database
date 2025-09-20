from django.contrib import admin

# Register your models here.

from .models import Contact, Tower, ContactMap, ContactMethod


class ContactMethodInline(admin.TabularInline):
	model = ContactMethod
	extra = 1

class ContactInline(admin.TabularInline):
	model = Tower.other_contacts.through
	verbose_name = "other contact"
	extra = 1

class ContactAdmin(admin.ModelAdmin):
	inlines = [ContactMethodInline]

class TowerAdmin(admin.ModelAdmin):
	inlines = [ContactInline]
	list_display = ["place", "dedication", "district", "bells"]
	list_filter = ["district", "bells", "ringing", "ring_type", "day", "report"]
	search_fields = ["place", "dedication"]

admin.site.register(Contact, ContactAdmin)
admin.site.register(Tower, TowerAdmin)


