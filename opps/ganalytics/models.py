# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django.db import models

from googleanalytics.account import  filter_operators

from opps.core.models import Publishable, Date

FIELDS_FILTER = ['pageviews', 'pagePath']


class Filter(Date):
    field = models.CharField(_(u"Field"), max_length=50,
                             choices=zip(FIELDS_FILTER, FIELDS_FILTER))
    operator = models.CharField(_(u"Operator"), choices=zip(filter_operators,
                                                            filter_operators),
                                max_length=3)
    expression = models.CharField(_(u"Expression"), max_length=255,
                                  help_text=_(u'Regular expression'))
    combined = models.CharField(_(u"Combined"), max_length=3, null=True,
                                blank=True, choices=(('OR','OR'),
                                                     ('AND','AND')))


class QueuryFilter(models.Model):
    query = models.ForeignKey('ganalytics.Query',
                              verbose_name=_(u'Query'),
                              null=True, blank=True,
                              related_name='queryfilter_queries',
                              on_delete=models.SET_NULL)
    filter = models.ForeignKey('ganalytics.Filter',
                               verbose_name=_('Filter'),
                               null=True, blank=True,
                               related_name='queryfilter_filters',
                               on_delete=models.SET_NULL)
    order = models.PositiveIntegerField(_(u'Order'), default=0)

    def __unicode__(self):
        return self.query.name


class Query(Publishable):
    name = models.CharField(_(u"Name"), max_length=140)
    start_date = models.DateTimeField(_(u"Start date"))
    end_date = models.DateTimeField(_(u"End date"))
    metrics = models.CharField(_(u"Metrics"), choices=(
        ('pageviews','Pageviews'),
        ('uniquepageviews','Unique Pageviews')), max_length=15)
    filter = models.ManyToManyField('ganalytics.Filter', null=True,
                                    blank=True, related_name='query_filters',
                                    through='ganalytics.QueuryFilter')
