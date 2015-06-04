#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf import settings

from appconf import AppConf


class OppsGAnalyticsConf(AppConf):

    RUN_EVERY_HOUR = getattr(
        settings, 'OPPS_GANALYTICS_RUN_EVERY_HOUR', 4)
    RUN_EVERY_MINUTE = getattr(
        settings, 'OPPS_GANALYTICS_RUN_EVERY_MINUTE', 30)
    RUN_EVERY_DAY_OF_WEEK = getattr(
        settings, 'OPPS_GANALYTICS_RUN_EVERY_DAY_OF_WEEK', "*")

    ACCOUNT = getattr(
        settings, "OPPS_GANALYTICS_ACCOUNT", "")

    PRIVATE_KEY = getattr(
        settings, "OPPS_GANALYTICS_PRIVATE_KEY", "")

    class Meta:
        prefix = 'opps_ganalytics'
