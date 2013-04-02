# -*- coding: utf-8 -*-
from django import template

register = template.Library()

@register.simple_tag
def get_top_read(number=10, channel_slug=None,
                template_name='ganalytics/top_read.html'):

    top_read = Report.objects.all()
    if channel_slug:
        top_read = top_read.filter(article__channel_slug=channel_slug)

    top_read = top_read[:number]

    t = template.loader.get_template(template_name)

    return t.render(template.Context({'top_read': top_read,
                                      'channel_slug': channel_slug}))
