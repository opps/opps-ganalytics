import pkg_resources
from django.utils.translation import ugettext_lazy as _
from django.conf import settings


pkg_resources.declare_namespace(__name__)

trans_app_label = _(u'Google Analytics')

VERSION = (0, 1, 0)

__version__ = ".".join(map(str, VERSION))
__status__ = "Development"
__description__ = u"Google Analytics for Opps CMS"
__author__ = u"Thiago Avelino"
__credits__ = []
__email__ = u"thiagoavelinoster@gmail.com"
__copyright__ = u"Copyright 2013, YACOWS"


settings.OPPS_GANALYTICS_ACCOUNT = getattr(settings,
                                           'OPPS_GANALYTICS_ACCOUNT', '')
settings.OPPS_GANALYTICS_PASSWORD = getattr(settings,
                                            'OPPS_GANALYTICS_PASSWORD', '')
settings.OPPS_GANALYTICS_APIKEY = getattr(settings,
                                          'OPPS_GANALYTICS_APIKEY', '')
