# -*- coding: utf-8 -*-
from collections import OrderedDict

from django import template
from django.conf import settings
from django.core.cache import cache
from django.db.models import Sum
from django.utils import timezone
from opps.containers.models import Container
from opps.ganalytics.models import Report

register = template.Library()


@register.simple_tag(takes_context=True)
def get_top_read(
        context, number=10, channel_slug=None, child_class=None,
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
        container__isnull=False,
        container__date_available__range=(start, now),
        container__published=True,
    ).order_by('-pageview')

    if channel_slug:
        top_read = top_read.filter(
            container__channel_long_slug__icontains=channel_slug
        )

    if child_class:
        top_read = top_read.filter(container__child_class=child_class)

    # to avoid repetitions annotate acts like group_by
    top_read = top_read.distinct().values(
        'container'
    ).annotate(Sum('pageview'))[:number]

    # as values returns a dict with pk only, needs to get the instance
    for top in top_read:
        top['container'] = Container.objects.get(pk=top['container'])

    t = template.loader.get_template(template_name)

    render = t.render(template.Context({
        'top_read': top_read,
        'channel_slug': channel_slug,
        'number': number,
        'context': context}))

    cache.set(cachekey, render, settings.OPPS_CACHE_EXPIRE * 60)

    return render


@register.simple_tag(takes_context=True)
def get_channels_top_read(context, *channels, **kwargs):
    template_name = kwargs.get(
        'template_name', 'ganalytics/channel_top_read.html')

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

    top_read = Report.objects.filter(
        container__isnull=False,
        container__published=True,
        container__date_available__range=(start, now),
        container__channel_long_slug__in=channels,
    ).order_by('-pageview')

    top_read = top_read.distinct().values(
        'container'
    ).annotate(Sum('pageview'))
    tops = {}

    # get one from each channel
    for top in top_read:
        container = Container.objects.get(pk=top['container'])
        top['container'] = container
        if container.channel_long_slug not in tops:
            tops[container.channel_long_slug] = top

    ordered = OrderedDict(
        sorted(
            tops.items(),
            key=lambda item: item[1]['pageview__sum'],
            reverse=True)
    )
    t = template.loader.get_template(template_name)

    render = t.render(template.Context(
        {'top_read': ordered, 'context': context}))

    cache.set(cachekey, render, settings.OPPS_CACHE_EXPIRE * 60)

    return render
