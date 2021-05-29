# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime

from apiclient.discovery import build
from celery.decorators import periodic_task
from celery.task.schedules import crontab
from django.contrib.sites.models import Site
from django.db import transaction
from django.utils import timezone
from httplib2 import Http
from oauth2client.client import SignedJwtAssertionCredentials
from urlparse import urlparse

from .conf import settings
from .models import Account, Query, Report


def ga_factory():
    """
    Returns googleapi object using server-side authentication."""

    with open(settings.OPPS_GANALYTICS_PRIVATE_KEY) as f:
        private_key = f.read()
    credentials = SignedJwtAssertionCredentials(
        settings.OPPS_GANALYTICS_ACCOUNT, private_key,
        'https://www.googleapis.com/auth/analytics.readonly')
    http_auth = credentials.authorize(Http())
    return build('analytics', 'v3', http=http_auth)


@transaction.commit_on_success
@periodic_task(
    run_every=crontab(
        hour=settings.OPPS_GANALYTICS_RUN_EVERY_HOUR,
        minute=settings.OPPS_GANALYTICS_RUN_EVERY_MINUTE,
        day_of_week=settings.OPPS_GANALYTICS_RUN_EVERY_DAY_OF_WEEK))
def get_accounts():
    if not settings.OPPS_GANALYTICS_STATUS:
        return None

    ga = ga_factory()

    accounts = ga.management().accounts().list().execute()

    # Verify all available accounts
    for a in accounts.get('items'):
        profiles = ga.management().profiles().list(
            accountId=a['id'], webPropertyId='~all').execute()

        # Verify all available profiles into account
        for p in profiles.get('items'):

            # Create account/profile if not exists.
            obj, create = Account.objects.get_or_create(
                account_id=a['id'], profile_id=p['id'],
                defaults={'account_name': a['name'], 'title': p['name']})

            # Update their titles
            if not create:
                obj.account_name = a['name']
                obj.title = p['name']
                obj.save()


@transaction.commit_on_success
@periodic_task(
    run_every=crontab(
        hour=settings.OPPS_GANALYTICS_RUN_EVERY_HOUR,
        minute=settings.OPPS_GANALYTICS_RUN_EVERY_MINUTE,
        day_of_week=settings.OPPS_GANALYTICS_RUN_EVERY_DAY_OF_WEEK),
    bind=True)
def get_metadata(self, verbose=False):
    if not settings.OPPS_GANALYTICS_STATUS:
        return None

    ga = ga_factory()

    default_site = Site.objects.get(pk=1)
    default_domain = 'http://' + default_site.domain

    query = Query.objects.filter(date_available__lte=timezone.now(),
                                 published=True)

    for q in query:
        params = {'ids': 'ga:{0}'.format(q.account.profile_id)}

        filters = q.formatted_filters()

        if filters:
            params['filters'] = filters

        params['start_date'] = datetime.date.today()
        if q.start_date:
            params['start_date'] = datetime.date(q.start_date.year,
                                                 q.start_date.month,
                                                 q.start_date.day)

        params['end_date'] = datetime.date.today()
        if q.end_date:
            params['end_date'] = datetime.date(q.end_date.year,
                                               q.end_date.month,
                                               q.end_date.day)

        params['metrics'] = 'ga:pageviews,ga:timeOnPage,ga:entrances'
        params['dimensions'] = 'ga:pageTitle,ga:pagePath'
        params['sort'] = '-ga:pageviews'
        params['max_results'] = 10000

        def cleanup_params(params):
            p = params.copy()
            for k in p:
                if not isinstance(p[k], basestring):
                    p[k] = unicode(p[k])
            return p

        data = []
        count_data = 0
        while count_data == 0:
            data = ga.data().ga().get(**cleanup_params(params)).execute()

            params['start_date'] -= datetime.timedelta(days=1)
            params['end_date'] -= datetime.timedelta(days=1)

            count_data = data['totalResults']

        # TITLE = 0
        URL, PAGEVIEWS, TIMEONPAGE, ENTRANCES = 1, 2, 3, 4

        for row in data.get('rows', []):
            url = row[URL][:255]

            if url.startswith('/'):
                url = default_domain + url

            if not url.startswith("http"):
                url = "http://" + url

            _url = urlparse(url)

            url = "{url.scheme}://{url.netloc}{url.path}".format(url=_url)

            report, create = Report.objects.get_or_create(url=url)

            if report:
                report.pageview = row[PAGEVIEWS]
                report.timeonpage = row[TIMEONPAGE]
                report.entrances = row[ENTRANCES]
                report.save()
