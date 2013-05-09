from django.contrib import admin

from .models import Criteria, Flag


class CriteriaAdmin(admin.ModelAdmin):
    model = Criteria
    readonly_fields = ('created', 'modified',)
    fieldsets = (
        (None, {
            'fields': ('name', 'flags', ('persistent', 'max_cookie_age'))}),
        ('Active For', {
            'fields': ('everyone', 'testing', 'percent', 'superusers',
                       'staff', 'authenticated', 'users', 'groups')}),
        ('Browsing', {
            'classes': ('collapse',),
            'fields': ('device_type', 'entry_url', 'referrer',
                       'query_args',)}),
        ('Details', {
            'classes': ('collapse',),
            'fields': ('note', 'created', 'modified')}),
    )

class FlagAdmin(admin.ModelAdmin):
    model = Flag
    readonly_fields = ('created', 'modified',)

admin.site.register(Criteria, CriteriaAdmin)
admin.site.register(Flag, FlagAdmin)
