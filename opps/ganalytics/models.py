# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django.db import models

from googleanalytics.account import filter_operators
from appconf import AppConf

from opps.core.models import Publishable, Date
from opps.articles.models import Article


FIELDS_FILTER = ['pageviews', 'pagePath']


class GAnalyticsConf(AppConf):
    ACCOUNT = ''
    PASSWORD = ''
    APIKEY = ''

    class Meta:
        prefix = 'opps_ganalytics'


class Filter(Date):
    field = models.CharField(_(u"Field"), max_length=50,
                             choices=zip(FIELDS_FILTER, FIELDS_FILTER))
    operator = models.CharField(_(u"Operator"), choices=zip(filter_operators,
                                                            filter_operators),
                                max_length=3)
    expression = models.CharField(_(u"Expression"), max_length=255,
                                  help_text=_(u'Regular expression'))
    combined = models.CharField(_(u"Combined"), max_length=3, null=True,
                                blank=True, choices=(('OR', 'OR'),
                                                     ('AND', 'AND')))


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
    account = models.ForeignKey('ganalytics.Account')
    start_date = models.DateTimeField(_(u"Start date"), null=True, blank=True)
    end_date = models.DateTimeField(_(u"End date"), null=True, blank=True)
    metrics = models.CharField(_(u"Metrics"), choices=(
        ('pageviews', 'Pageviews'),
        ('uniquepageviews', 'Unique Pageviews')), max_length=15)
    filter = models.ManyToManyField('ganalytics.Filter', null=True,
                                    blank=True, related_name='query_filters',
                                    through='ganalytics.QueuryFilter')

    def __unicode__(self):
        return u"{0}-{1}".format(self.account.title, self.name)


class Report(Date):
    url = models.CharField(_('URL'), max_length=255, unique=True)

    # Get Google Analytics
    pageview = models.IntegerField(default=0)
    timeonpage = models.CharField(_(u'Time on page'), max_length=25, default=0)
    entrances = models.IntegerField(default=0)

    # Opps join
    article = models.ForeignKey('articles.Article', null=True, blank=True,
                                related_name='report_articles',
                                on_delete=models.SET_NULL)

    def save(self, *args, **kwargs):
        def _domain(sefl, domain):
            if ':' in domain:
                return domain.split(':', 1)[0]
            return domain

        try:
            not_domian = self.url.replace(self.url.split('/')[0], '')
            slug = not_domian.split('/')[-1]
            article = Article.objects.filter(slug=slug, site__domain=_domain(self.url.split('/')[0]))
            for a in article:
                if a.channel.long_slug in not_domian.replace(slug, ''):
                    self.article = a
                    break
        except:
            pass

        super(Report, self).save(*args, **kwargs)


class Account(Date):
    account_id = models.IntegerField()
    account_name = models.CharField(_(u"Account name"), max_length=150)
    title = models.CharField(_(u'Title'), max_length=255)
    profile_id = models.IntegerField(unique=True)

    def __unicode__(self):
        return u"{0}-{1}".format(self.title, self.profile_id)
