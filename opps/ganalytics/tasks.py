# -*- coding: utf-8 -*-
import datetime

from django.utils import timezone
from django.conf import settings

from celery.decorators import periodic_task
from celery.task.schedules import crontab
from googleanalytics import Connection

from .models import Query, QueuryFilter, Report, Account


@periodic_task(run_every=crontab(hour="*", minute="*", day_of_week="*"))
def get_accounts():
    connection = Connection(settings.OPPS_GANALYTICS_ACCOUNT,
                            settings.OPPS_GANALYTICS_PASSWORD,
                            settings.OPPS_GANALYTICS_APIKEY)

    accounts = connection.get_accounts()

    for a in accounts:
        obj, create = Account.objects.get_or_create(profile_id=a.profile_id,
                                                    account_id=a.account_id,
                                                    account_name=a.account_name,
                                                    title=a.title)
        if not create:
            obj.account_id = a.account_id
            obj.account_name = a.account_name
            obj.title = a.title
            obj.save()


@periodic_task(run_every=crontab(hour="*/4", minute="*", day_of_week="*"))
def get_metadata():
    connection = Connection(settings.OPPS_GANALYTICS_ACCOUNT,
                            settings.OPPS_GANALYTICS_PASSWORD,
                            settings.OPPS_GANALYTICS_APIKEY)

    query = Query.objects.filter(date_available__lte=timezone.now(),
                                 published=True)

    for q in query:
        account = connection.get_account('{0}'.format(q.account.profile_id))

        filters = [[f.filter.field,
                    f.filter.operator,
                    f.filter.expression,
                    f.filter.combined or '']
                   for f in QueuryFilter.objects.filter(query=query)]

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
        data = account.get_data(start_date, end_date, metrics=metrics,
                                dimensions=dimensions, filters=filters,
                                max_results=1000, sort=['-pageviews'])

        for row in data.list:
            report, create = Report.objects.get_or_create(url=row[0][1])
            if report:
                report.pageview = row[1][0]
                report.timeonpage = row[1][1]
                report.entrances = row[1][2]
                report.save()
