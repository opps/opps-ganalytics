# opps.ganalytics

[![Build
Status](https://travis-ci.org/opps/opps-ganalytics.png?branch=master)](https://travis-ci.org/opps/opps-ganalytics)

_Opps Google Analytics Application_

- Access Google Analytics API
- Filters
- Template tag

## Dependencies

- RabbitMQ (Celery)

## Requirements

- opps
- django-celery
- google-api-python-client

## Settings var

- OPPS*GANALYTICS_ACCOUNT - \_Generated email by [service account](https://developers.google.com/identity/protocols/OAuth2ServiceAccount) credencial. (example: @developer.gserviceaccount.com)*
- OPPS*GANALYTICS_PRIVATE_KEY -\_path to .pem key, converted from service account .p12 key, [see more.](http://stackoverflow.com/questions/17993604/signedjwtassertioncredentials-on-appengine-doesnt-recognize-pem-key)*

## Task

- Get accounts - _Get all Google Analytics Accounts_
- Get metadata - _Sync metadata, run 4 in 4 hours_
