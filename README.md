opps.ganalytics
===============

[![Build
Status](https://travis-ci.org/opps/opps-ganalytics.png?branch=master)](https://travis-ci.org/opps/opps-ganalytics)

_Opps Google Analytics Application_

* Access Google Analytics API
* Filters
* Template tag


## Dependencies

* RabbitMQ (Celery)


## Requirements

* opps
* django-celery
* [python-googleanalytics](http://github.com/avelino/python-googleanalytics)


## Settings var

* OPPS_GANALYTICS_ACCOUNT - _Valid email Google (example: @gmail.com)_
* OPPS_GANALYTICS_PASSWORD - _Account password_
* OPPS_GANALYTICS_APIKEY - _Get APIKEY on [Google API Console](https://code.google.com/apis/console/)_


## Task

* Get accounts - _Get all Google Analytics Accounts_
* Get metadata - _Sync metadata, run 4 in 4 hours_

