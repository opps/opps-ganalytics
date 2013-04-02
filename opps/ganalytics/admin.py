# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Filter, Query, QueuryFilter, Report, Account


class QueuryFilterInline(admin.TabularInline):
    model = QueuryFilter
    fk_name = 'query'
    raw_id_fields = ['filter']
    actions = None
    extra = 1
    fieldsets = [(None, {
        'classes': ('collapse',),
        'fields': ('filter', 'order')})]


class FilterAdmin(admin.ModelAdmin):
    list_display = ['field', 'operator', 'expression', 'combined']


class QueryAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_date', 'end_date', 'metrics', 'account']
    inlines = [QueuryFilterInline]
    raw_id_fields = ['account']


class ReportAdmin(admin.ModelAdmin):
    list_display = ['url', 'pageview', 'article']
    search_fields = ['url']
    raw_id_fields = ['article']


class AccountAdmin(admin.ModelAdmin):
    list_display = ['title', 'account_name', 'profile_id']
    search_fields = ['title', 'account_name', 'profile_id']


admin.site.register(Filter, FilterAdmin)
admin.site.register(Query, QueryAdmin)
admin.site.register(Report, ReportAdmin)
admin.site.register(Account, AccountAdmin)
