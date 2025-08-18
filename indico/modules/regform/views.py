# This file is part of Indico.
# Copyright (C) 2002 - 2025 CERN
#
# Indico is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see the
# LICENSE file for more details.

from indico.modules.events.management.views import WPEventManagement
from indico.modules.events.models.events import EventType
from indico.modules.events.views import WPConferenceDisplayBase, WPSimpleEventDisplayBase
from indico.web.views import WPJinjaMixin


class WPManageRegistrationStats(WPManageRegistration):
    bundles = ('statistics.js', 'statistics.css')


class DisplayRegistrationFormMixin(WPJinjaMixin):
    template_prefix = 'events/registration/'
    base_class = None

    def _get_body(self, params):
        return WPJinjaMixin._get_page_content(self, params)


class WPDisplayRegistrationFormConference(DisplayRegistrationFormMixin, WPConferenceDisplayBase):
    template_prefix = 'events/registration/'
    base_class = WPConferenceDisplayBase
    menu_entry_name = 'registration'
    bundles = ('module_events.registration.js', 'module_events.registration.css')


class WPDisplayRegistrationFormSimpleEvent(DisplayRegistrationFormMixin, WPSimpleEventDisplayBase):
    template_prefix = 'events/registration/'
    base_class = WPSimpleEventDisplayBase
    bundles = ('module_events.registration.js', 'module_events.registration.css')
