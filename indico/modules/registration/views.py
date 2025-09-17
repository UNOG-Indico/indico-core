# This file is part of Indico.
# Copyright (C) 2002 - 2025 CERN
#
# Indico is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see the
# LICENSE file for more details.

from indico.web.flask.util import url_for
from indico.modules.categories.views import WPCategoryManagement
from indico.modules.events.management.views import WPEventManagement
from indico.modules.events.models.events import EventType
from indico.modules.events.views import WPConferenceDisplayBase, WPSimpleEventDisplayBase
from indico.web.views import WPJinjaMixin


class WPEventManageRegistration(WPEventManagement):
    template_prefix = 'registration/'
    bundles = ('module_registration.js', 'module_registration.css', 'module_receipts.js',
               'module_receipts.css')

    def __init__(self, rh, event_, active_menu_item=None, **kwargs):
        self.regform = kwargs.get('regform')
        self.registration = kwargs.get('registration')
        WPEventManagement.__init__(self, rh, event_, active_menu_item, **kwargs)

    @property
    def sidemenu_option(self):
        if self.event.type_ != EventType.conference:
            regform = self.regform
            if not regform:
                if self.registration:
                    regform = self.registration.registration_forms
            if regform and regform.is_participation:
                return 'participants'
        return 'registration'


class WPCategoryManageRegistration(WPCategoryManagement):
    template_prefix = 'registration/'
    bundles = ('module_registration.js', 'module_registration.css', 'module_receipts.js',
               'module_receipts.css')

    def __init__(self, rh, category, active_menu_item=None, **kwargs):
        self.regform = kwargs.get('regform')
        WPCategoryManagement.__init__(self, rh, category, active_menu_item, **kwargs)

    def _get_parent_category_breadcrumb_url(self, category, management=False):
        if not management:
            return category.url
        # we don't want template-specific urls since those may be tied
        # to the previous category
        return url_for('event_registration.manage_regform_list', category)


class WPManageRegistrationStats(WPEventManageRegistration):
    bundles = ('statistics.js', 'statistics.css')


class WPManageParticipants(WPEventManageRegistration):
    sidemenu_option = 'participants'


class DisplayRegistrationFormMixin(WPJinjaMixin):
    template_prefix = 'registration/'
    base_class = None

    def _get_body(self, params):
        return WPJinjaMixin._get_page_content(self, params)


class WPDisplayRegistrationFormConference(DisplayRegistrationFormMixin, WPConferenceDisplayBase):
    template_prefix = 'registration/'
    base_class = WPConferenceDisplayBase
    menu_entry_name = 'registration'
    bundles = ('module_registration.js', 'module_registration.css')


class WPDisplayRegistrationParticipantList(WPDisplayRegistrationFormConference):
    menu_entry_name = 'participants'


class WPDisplayRegistrationFormSimpleEvent(DisplayRegistrationFormMixin, WPSimpleEventDisplayBase):
    template_prefix = 'registration/'
    base_class = WPSimpleEventDisplayBase
    bundles = ('module_registration.js', 'module_registration.css')
