# This file is part of Indico.
# Copyright (C) 2002 - 2025 CERN
#
# Indico is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see the
# LICENSE file for more details.

from datetime import datetime

from _decimal import Decimal
from pytz import timezone

from indico.util.date_time import format_currency
from indico.util.locators import locator_property


class Dummy:
    """Lightweight dummy object."""
    pass


class DummyRegistration(Dummy):
    def get_summary_data(self, hide_empty=False):
        return {}

    def render_price(self):
        return format_currency(self.price, self.currency)

    def get_locator_dict(self):
        return dict(reg_form_id=self.registration_form.id, registration_id=self.id, event_id=self.event.id)

    @locator_property
    def locator(self):
        return self.get_locator_dict()

    @locator.registrant
    def locator(self):
        locator = self.get_locator_dict()
        del locator['registration_id']
        locator['token'] = 'd8343'
        return locator


def get_dummy_registration():
    """Return a full dummy registration object using Dummy class."""
    reg = DummyRegistration()

    # Basic fields
    reg.id = 123
    reg.first_name = 'John'
    reg.last_name = 'Doe'
    reg.full_name = f'{reg.first_name} {reg.last_name}'
    reg.email = 'john.doe@example.com'
    reg.price = 150
    reg.friendly_id = 123
    reg.data = []
    reg.summary_data = {}
    reg.price = Decimal('0')
    reg.currency = 'EUR'

    # state object
    reg.state = Dummy()
    reg.state.title = 'Complete'

    # Methods
    reg.get_full_name = lambda: reg.full_name
    reg.get_base_price = lambda: reg.price

    # Registration Form
    reg.registration_form = Dummy()
    reg.registration_form.id = 123
    reg.registration_form.title = 'Demo Registration Form'
    reg.registration_form.currency = 'CHF'

    # Event
    reg.event = Dummy()
    reg.event.id = 123
    reg.event.title = 'Demo Conference 2025'
    reg.event.start_dt = datetime.fromisoformat('2025-02-15 09:00')
    reg.event.end_dt = datetime.fromisoformat('2025-02-17 17:00')
    reg.event.timezone = 'Europe/Zurich'
    reg.event.external_url = 'www.example.com'
    reg.event.start_dt_local = reg.event.start_dt
    reg.event.end_dt_local = reg.event.end_dt
    reg.event.tzinfo = timezone(reg.event.timezone)
    reg.registration_form.event = reg.event
    return reg
