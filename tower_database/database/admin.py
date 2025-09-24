from django.contrib import admin

from search_admin_autocomplete.admin import SearchAutoCompleteAdmin

# Register your models here.

from .models import Contact, Tower, ContactMap, Website

admin.site.site_header = "Ely DA Tower Database"
admin.site.site_title = "Database admin"
admin.site.index_title = "Database admin"


class ContactInline(admin.TabularInline):
    model = Tower.other_contacts.through
    verbose_name = "other contact"
    extra = 0
    #classes = ["collapse"]

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
    #classes = ["collapse"]

class ContactAdmin(SearchAutoCompleteAdmin):
    inlines= [PrimaryContactInline, TowerInline]
    search_fields = ["name", "phone", "email"]
    search_help_text = "Search by name, phone number or email"

class TowerAdmin(SearchAutoCompleteAdmin):
    inlines = [WebsiteInline, ContactInline]
    list_display = ["place", "dedication", "district", "bells"]
    list_filter = ["district", "report", "bells", "ringing_status", "ring_type", "practice_day"]
    search_fields = ["place", "dedication", "full_dedication", "nickname"]
    search_help_text = "Search by place or dedication"
    fieldsets = [
        (
            None, {
                "fields": (
                    "place",
                    "county",
                    "dedication",
                    "include_dedication",
                    "full_dedication",
                    "nickname",
                    "district",
                    "report",
                    "peals",
                )
            }
        ),
        (
            "Ringing", {
                "fields": (
                    "ringing_status",
                    "service",
                    "practice",
                    "practice_day",
                    "practice_weeks",
                    "travel_check",
                )
            }
        ),
        (
            "Bells", {
                "fields": (
                    "bells",
                    "ring_type",
                    "weight",
                    "note",
                    "gf",
                )
            }
        ),
        (
            "Location", {
                "fields": (
                    "os_grid",
                    "postcode",
                    "lat",
                    "lng",
                )
            }
        ),
        (
            "Contacts, links and notes", {
                "fields": (
                    "primary_contact",
                    "contact_use",
                    "dove_towerid",
                    "dove_ringid",
                    "towerbase_id",
                    "notes",
                    "long_notes",
                    "maintainer_notes",
                )
            }
        )
    ]

admin.site.register(Contact, ContactAdmin)
admin.site.register(Tower, TowerAdmin)

