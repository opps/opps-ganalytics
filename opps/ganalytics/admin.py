# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Filter, Query, QueuryFilter, Report


class QueuryFilterInline(admin.TabularInline):
    model = QueuryFilter
    fk_name = 'query'
    raw_id_fields = ['filter']
    actions = None
    extra = 1
    fieldsets = [(None, {
        'classes': ('collapse',),
        'fields': ('filter', 'order')})]


class QueryAdmin(admin.ModelAdmin):
    inlines = [QueuryFilterInline]

admin.site.register(Filter)
admin.site.register(Query, QueryAdmin)
admin.site.register(Report)
