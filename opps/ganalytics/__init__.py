import pkg_resources

pkg_resources.declare_namespace(__name__)

VERSION = (0, 2, 7)

__version__ = ".".join(map(str, VERSION))
__status__ = "Development"
__description__ = u"Google Analytics for Opps CMS"
__author__ = u"Thiago Avelino"
__credits__ = ['Jean Rodrigues']
__email__ = u"avelinorun@gmail.com"
__copyright__ = u"Copyright 2015, Opps CMS"
