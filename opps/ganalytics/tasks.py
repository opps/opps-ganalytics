# -*- coding: utf-8 -*-
import datetime
from ssl import SSLError
from urlparse import urlparse
from httplib2 import Http

from django.utils import timezone
from django.db import transaction
from django.contrib.sites.models import Site

from celery.decorators import periodic_task
from celery.task.schedules import crontab
from oauth2client.client import SignedJwtAssertionCredentials
from apiclient.discovery import build

from .models import Query, QueryFilter, Report, Account
from .conf import settings


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
                account_id=a['id'], profile_id=p['id'])

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

    if verbose:
        print('getting get_metadata')

    if not settings.OPPS_GANALYTICS_STATUS:
        return None

    ga = ga_factory()

    connection = Connection(settings.OPPS_GANALYTICS_ACCOUNT,
                            settings.OPPS_GANALYTICS_PASSWORD,
                            settings.OPPS_GANALYTICS_APIKEY)

    if verbose:
        print(connection)

    default_site = Site.objects.get(pk=1)
    default_domain = 'http://' + default_site.domain

    query = Query.objects.filter(date_available__lte=timezone.now(),
                                 published=True)

    if verbose:
        print(query)

    for q in query:
        if verbose:
            print(q.name)

        account = connection.get_account('{0}'.format(q.account.profile_id))

        if verbose:
            print(account)

        filters = [[f.filter.field,
                    f.filter.operator,
                    f.filter.expression,
                    f.filter.combined or '']
                   for f in QueryFilter.objects.filter(query=q)]

        if verbose:
            print(filters)

        start_date = datetime.date.today()
        if q.start_date:
            start_date = datetime.date(q.start_date.year,
                                       q.start_date.month,
                                       q.start_date.day)
        end_date = datetime.date.today()
        if q.end_date:
            end_date = datetime.date(q.end_date.year,
                                     q.end_date.month,
                                     q.end_date.day)
        metrics = ['pageviews', 'timeOnPage', 'entrances']
        dimensions = ['pageTitle', 'pagePath']

        data = []
        count_data = len(data)
        while count_data == 0:
            try:
                data = account.get_data(start_date, end_date, metrics=metrics,
                                        dimensions=dimensions, filters=filters,
                                        max_results=1000, sort=['-pageviews'])
            except SSLError as exc:
                raise self.retry(exc=exc)

            start_date -= datetime.timedelta(days=1)
            end_date -= datetime.timedelta(days=1)
            count_data = len(data)

        # print  len(data.list)
        if verbose:
            print(len(data.list))

        for row in data.list:
            if verbose:
                print("ROW:")
                print(row)

            try:
                url = row[0][1][:255]
                if verbose:
                    print("URL:")
                    print(url)

                if url.startswith('/'):
                    url = default_domain + url

                if not url.startswith("http"):
                    url = "http://" + url

                _url = urlparse(url)

                url = "{url.scheme}://{url.netloc}{url.path}".format(url=_url)
                if verbose:
                    print(url)

                report, create = Report.objects.get_or_create(url=url)
                if verbose:
                    print(report)
                    print(create)

                if report:
                    report.pageview = row[1][0]
                    report.timeonpage = row[1][1]
                    report.entrances = row[1][2]
                    report.save()
                    if verbose:
                        print("CONTAINER:")
                        print(report.container)

            except Exception as e:
                if verbose:
                    print(str(e))
                pass
