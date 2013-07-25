# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Filter, Query, QueryFilter, Report, Account
from opps.core.admin import apply_opps_rules


class QueryFilterInline(admin.TabularInline):
    model = QueryFilter
    fk_name = 'query'
    raw_id_fields = ['filter']
    actions = None
    extra = 1
    fieldsets = [(None, {
        'classes': ('collapse',),
        'fields': ('filter', 'order')})]


@apply_opps_rules('ganalytics')
class FilterAdmin(admin.ModelAdmin):
    list_display = ['field', 'operator', 'expression', 'combined']


@apply_opps_rules('ganalytics')
class QueryAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_date', 'end_date', 'metrics', 'account']
    inlines = [QueryFilterInline]
    raw_id_fields = ['account']


@apply_opps_rules('ganalytics')
class ReportAdmin(admin.ModelAdmin):
    list_display = ['url', 'pageview', 'container', 'date_update']
    search_fields = ['url', 'container__channel_name', 'container__channel__slug',
                     'container__title']
    raw_id_fields = ['container']


@apply_opps_rules('ganalytics')
class AccountAdmin(admin.ModelAdmin):
    list_display = ['title', 'account_name', 'profile_id']
    search_fields = ['title', 'account_name', 'profile_id']


admin.site.register(Filter, FilterAdmin)
admin.site.register(Query, QueryAdmin)
admin.site.register(Report, ReportAdmin)
admin.site.register(Account, AccountAdmin)
