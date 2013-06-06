# -*- coding: utf-8 -*-
from django import template
from django.conf import settings
from django.db.models import Sum
from django.utils import timezone
from opps.ganalytics.models import Report
from opps.articles.models import Article


register = template.Library()


@register.simple_tag(takes_context=True)
def get_top_read(context, number=10, channel_slug=None, child_class=None,
                 template_name='ganalytics/top_read.html'):

    now = timezone.now()
    start = now - timezone.timedelta(days=settings.OPPS_GANALYTICS_RANGE_DAYS)

    top_read = Report.objects.filter(
        article__isnull=False,
        article__date_available__range=(start, now),
        article__published=True,
    ).order_by('-pageview')

    if channel_slug:
        top_read = top_read.filter(article__channel_long_slug=channel_slug)

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

    return t.render(template.Context({'top_read': top_read,
                                      'channel_slug': channel_slug,
                                      'number': number,
                                      'context': context}))
