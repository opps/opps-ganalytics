# -*- coding: utf-8 -*-
import datetime
from urlparse import urlparse

from django.utils import timezone
from django.conf import settings
from django.db import transaction

from celery.decorators import periodic_task
from celery.task.schedules import crontab
from googleanalytics import Connection

from .models import Query, QueryFilter, Report, Account


@periodic_task(run_every=crontab(hour=settings.OPPS_GANALYTICS_RUN_EVERY_HOUR,
                                 minute=settings.OPPS_GANALYTICS_RUN_EVERY_MINUTE,
                                 day_of_week=settings.OPPS_GANALYTICS_RUN_EVERY_DAY_OF_WEEK))
@transaction.commit_on_success
def get_accounts():
    if not settings.OPPS_GANALYTICS_STATUS:
        return None

    connection = Connection(settings.OPPS_GANALYTICS_ACCOUNT,
                            settings.OPPS_GANALYTICS_PASSWORD,
                            settings.OPPS_GANALYTICS_APIKEY)

    accounts = connection.get_accounts()

    for a in accounts:
        # # # print  a
        obj, create = Account.objects.get_or_create(profile_id=a.profile_id,
                                                    account_id=a.account_id,
                                                    account_name=a.account_name,
                                                    title=a.title)
        if not create:
            obj.account_id = a.account_id
            obj.account_name = a.account_name
            obj.title = a.title
            obj.save()


@periodic_task(run_every=crontab(hour=settings.OPPS_GANALYTICS_RUN_EVERY_HOUR,
                                 minute=settings.OPPS_GANALYTICS_RUN_EVERY_MINUTE,
                                 day_of_week=settings.OPPS_GANALYTICS_RUN_EVERY_DAY_OF_WEEK))
@transaction.commit_on_success
def get_metadata():
    if not settings.OPPS_GANALYTICS_STATUS:
        return None

    connection = Connection(settings.OPPS_GANALYTICS_ACCOUNT,
                            settings.OPPS_GANALYTICS_PASSWORD,
                            settings.OPPS_GANALYTICS_APIKEY)

    query = Query.objects.filter(date_available__lte=timezone.now(),
                                 published=True)

    for q in query:
        # print  q.name
        account = connection.get_account('{0}'.format(q.account.profile_id))

        filters = [[f.filter.field,
                    f.filter.operator,
                    f.filter.expression,
                    f.filter.combined or '']
                   for f in QueryFilter.objects.filter(query=q)]

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
            data = account.get_data(start_date, end_date, metrics=metrics,
                                    dimensions=dimensions, filters=filters,
                                    max_results=1000, sort=['-pageviews'])
            start_date -= datetime.timedelta(days=1)
            end_date -= datetime.timedelta(days=1)
            count_data = len(data)

        # print  len(data.list)

        for row in data.list:
            try:
                url = row[0][1][:255]

                if not url.startswith("http"):
                    url = "http://" + url

                _url = urlparse(url)

                url = "{url.scheme}://{url.netloc}{url.path}".format(url=_url)
                # print  url

                report, create = Report.objects.get_or_create(url=url)
                if report:
                    report.pageview = row[1][0]
                    report.timeonpage = row[1][1]
                    report.entrances = row[1][2]
                    report.save()
                    # print  report.article
            except:
                # # print  str(e)
                pass
