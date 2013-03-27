# -*- coding: utf-8 -*-
import datetime

from django.utils import timezone
from django.conf import settings

from celery import task
from celery.decorators import periodic_task
from celery.task.schedules import crontab
from googleanalytics import Connection

from .models import Query, QueuryFilter


@periodic_task(run_every=crontab(hour="*", minute="*", day_of_week="*"))
def get_metadata():
    connection = Connection(settings.OPPS_GANALYTICS_ACCOUNT,
                            settings.OPPS_GANALYTICS_PASSWORD,
                            settings.OPPS_GANALYTICS_APIKEY)
    account = connection.get_account('26913582')

    query = Query.objects.filter(date_available__lte=timezone.now(),
                                 published=True)

    for q in query:
        filters = [[f.filter.field, f.filter.operator, f.filter.expression] \
                   for f in QueuryFilter.objects.filter(query=query)]

        start_date = datetime.date(q.start_date.year,
                                   q.start_date.month,
                                   q.start_date.day)
        end_date = datetime.date(q.end_date.year,
                                 q.end_date.month,
                                 q.end_date.day)
        metrics = ['pageviews', 'timeOnPage', 'entrances']
        dimensions = ['pageTitle', 'pagePath']
        data = account.get_data(start_date, end_date, metrics=metrics,
                                dimensions=dimensions, filters=filters,
                                max_results=10, sort=['-pageviews',])

        for row in data.list:
            print row[0]
            print row[1]
            print "\n\n"
