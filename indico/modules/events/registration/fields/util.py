# This file is part of Indico.
# Copyright (C) 2002 - 2025 CERN
#
# Indico is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see the
# LICENSE file for more details.

from datetime import datetime


def to_machine_date(date):
    return date.strftime('%Y-%m-%d')


def to_date(date):
    return datetime.strptime(date, '%Y-%m-%d').date()
