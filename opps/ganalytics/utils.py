# -*- coding: utf-8 -*-

from __future__ import unicode_literals


FILTER_OPERATORS = ['==', '!=', '>', '<', '>=', '<=', '=~', '!~', '=@', '!@']


def process_filters(filters):
    processed_filters = []
    multiple_filters = False
    if len(filters) > 1:
        multiple_filters = True
    for filt in filters:
        if len(filt) < 3:
            continue
        if len(filt) == 3:
            name, operator, expression = filt
            if multiple_filters:
                comb = 'AND'
            else:
                comb = ''
        elif len(filt) == 4:
            name, operator, expression, comb = filt
            if comb != 'AND' and comb != 'OR':
                comb == 'AND'

        # Reject any filters with invalid operators
        if operator not in FILTER_OPERATORS:
            continue

        name = 'ga:' + name

        # Mapping to GA's boolean operators
        if comb == 'AND':
            comb = ';'
        if comb == 'OR':
            comb = ','

        # These three characters are special and must be escaped
        if '\\' in expression:
            expression = expression.replace('\\', '\\\\')
        if ',' in expression:
            expression = expression.replace(',', '\,')
        if ';' in expression:
            expression = expression.replace(';', '\;')

        processed_filters.append("".join([name, operator, expression, comb]))
    filter_string = "".join(processed_filters)

    # Strip any trailing boolean symbols
    if filter_string:
        if filter_string[-1] == ';' or filter_string[-1] == ',':
            filter_string = filter_string[:-1]
    return filter_string
