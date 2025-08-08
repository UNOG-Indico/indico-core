# This file is part of Indico.
# Copyright (C) 2002 - 2025 CERN
#
# Indico is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see the
# LICENSE file for more details.

from flask import session
from indico.core import signals
from indico.util.i18n import _
from indico.web.flask.util import url_for
from indico.web.menu import SideMenuItem


@signals.menu.items.connect_via('category-management-sidemenu')
def _sidemenu_items(sender, category, **kwargs):
    yield SideMenuItem('registration', _('Registration Forms'), url_for('categories.manage_regforms', category),  # would be regforms.manage_regforms? or regforms.manage_regform_list
                       40, icon='list')


@signals.menu.items.connect_via('event-management-sidemenu')
def _extend_event_management_menu(sender, event, **kwargs):
    registration_section = 'organization' if event.type == 'conference' else 'advanced'
    if not event.can_manage(session.user, 'registration'):
        return
    if event.has_feature('registration'):
        yield SideMenuItem('registration', _('Registration'), url_for('event_registration.manage_regform_list', event),
                           section=registration_section)
