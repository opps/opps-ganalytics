# -*- coding: utf-8 -*-
from collections import OrderedDict

from django import template
from django.conf import settings
from django.db.models import Sum
from django.utils import timezone
from django.core.cache import cache

from opps.ganalytics.models import Report
from opps.articles.models import Article
from opps.channels.models import Channel

register = template.Library()
SMART_SEARCH = getattr(settings, 'OPPS_GANALYTICS_SMART_SEARCH', True)


@register.simple_tag(takes_context=True)
def get_top_read(context, number=10, channel_slug=None, child_class=None,
                 template_name='ganalytics/top_read.html'):

    request = context['request']
    is_mobile = getattr(request, 'is_mobile', False)

    cachekey = "ga-gettopread-{}{}{}{}{}".format(
        number,
        channel_slug,
        child_class,
        template_name,
        is_mobile
    )

    render = cache.get(cachekey)
    if render:
        return render

    now = timezone.now()
    start = now - timezone.timedelta(days=settings.OPPS_GANALYTICS_RANGE_DAYS)

    top_read = Report.objects.filter(
        article__isnull=False,
        article__date_available__range=(start, now),
        article__published=True,
    ).order_by('-pageview')

    if channel_slug:
        if SMART_SEARCH:
            channel = channel_slug.split('/')[0]
            root_channel = Channel.objects.get(slug=channel).root.slug

            # searchs on root and parent channels
            lookup = dict(
                article__channel_long_slug__icontains=root_channel
            )
        else:
            # searchs only on current channel
            lookup = dict(article__channel_long_slug=channel_slug)
        top_read = top_read.filter(**lookup)

    if child_class:
        top_read = top_read.filter(article__child_class=child_class)

    # to avoid repetitions annotate acts like group_by
    top_read = top_read.distinct().values(
        'article'
    ).annotate(Sum('pageview'))[:number]

    # as values returns a dict with pk only, needs to get the instance
    for top in top_read:
        top['article'] = Article.objects.get(pk=top['article'])

    t = template.loader.get_template(template_name)

    render = t.render(template.Context({'top_read': top_read,
                                        'channel_slug': channel_slug,
                                        'number': number,
                                        'context': context}))
    cache.set(cachekey, render, 60 * 60)
    return render

@register.simple_tag(takes_context=True)
def get_channels_top_read(context, *channels, **kwargs):
    template_name = kwargs.get('template_name',
                               'ganalytics/channel_top_read.html')
    request = context['request']
    is_mobile = getattr(request, 'is_mobile', False)

    cachekey = "ga-gettopread-{}{}{}".format(
        "-".join(channels),
        template_name,
        is_mobile
    )

    render = cache.get(cachekey)
    if render:
        return render

    now = timezone.now()
    start = now - timezone.timedelta(days=settings.OPPS_GANALYTICS_RANGE_DAYS)

    tops = {}
    for channel in channels:
        try:
            top_read = Report.objects.filter(
                article__isnull=False,
                article__published=True,
                article__date_available__range=(start, now),
                article__channel_long_slug__contains=channel,
            ).order_by('-pageview', '-article__date_available').latest('id')
        except Report.DoesNotExist:
            tops[channel] = None
            continue
        tops[channel] = top_read

    ordered = OrderedDict(
        sorted(tops.items(),
               key=lambda item: item[1].pageview if item[1] else 0,
               reverse=True)
    )
    template_name = kwargs.get('template_name',
                               'ganalytics/channel_top_read.html')

    t = template.loader.get_template(template_name)

    render = t.render(template.Context({'top_read': ordered,
                                        'context': context}))
    cache.set(cachekey, render, 60 * 60)
    return render
