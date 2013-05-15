from django.contrib import admin

from .models import Criteria, Flag


class CriteriaAdmin(admin.ModelAdmin):
    model = Criteria
    raw_id_fields = ('users', 'groups')
    readonly_fields = ('created', 'modified',)
    list_display = ('name', 'note', 'flag_names', 'persistent', 'everyone',
                    'testing', 'percent', 'superusers', 'staff',
                    'authenticated')
    fieldsets = (
        (None, {
            'fields': ('name', 'flags', ('persistent', 'max_cookie_age'))}),
        ('Active For', {
            'fields': ('everyone', 'testing', 'percent', 'superusers',
                       'staff', 'authenticated', 'users', 'groups')}),
        ('Browsing', {
            'classes': ('collapse',),
            'fields': ('entry_url', 'referrer', 'device_type',
                       'query_args',)}),
        ('Details', {
            'classes': ('collapse',),
            'fields': ('note', 'created', 'modified')}),
    )

    def flag_names(self, criteria):
        return ', '.join([f.name for f in criteria.flags.all()])
    flag_names.short_description = 'Flags'


class FlagAdmin(admin.ModelAdmin):
    model = Flag
    readonly_fields = ('created', 'modified',)

admin.site.register(Criteria, CriteriaAdmin)
admin.site.register(Flag, FlagAdmin)
