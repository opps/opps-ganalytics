from opps.ganalytics.models import Filter, Query, Account, QueryFilter
from opps.channels.models import Channel
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site

User = get_user_model()

channels = Channel.objects.filter(
    show_in_menu=True,
    parent__isnull=True
)


for channel in channels:
    if channel == channel.get_root():

        filter = Filter(
            field='pagePath',
            operator='=@',
            expression=u'/' + channel.long_slug,
            combined='AND'
        )

        filter.save()

        query = Query(
            user=User.objects.get(pk=1),
            site=Site.objects.get(pk=1),
            published=True,
            name=u"Top 10 {}".format(channel.name),
            account=Account.objects.get(pk=1),
            metrics='pageviews',
        )

        query.save()

        qf = QueryFilter(
            query=query,
            filter=filter,
            order=0
        )

        qf.save()

        try:
            qf2 = QueryFilter(
                query=query,
                filter=Filter.objects.get(pk=119),
                order=1
            )

            qf2.save()
        except:
            pass
