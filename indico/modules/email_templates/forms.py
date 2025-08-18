# This file is part of Indico.
# Copyright (C) 2002 - 2025 CERN
#
# Indico is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see the
# LICENSE file for more details.

from flask import request, session
from wtforms import BooleanField, HiddenField, SelectField, StringField, TextAreaField
from wtforms.validators import DataRequired, Length, ValidationError

from indico.util.i18n import _
from indico.util.placeholders import get_missing_placeholders, render_placeholder_info
from indico.web.forms.base import IndicoForm
from indico.web.forms.fields import EmailListField, HiddenFieldList, IndicoEmailRecipientsField, IndicoEnumSelectField
from indico.web.forms.validators import HiddenUnless, NoRelativeURLs
from indico.web.forms.widgets import SwitchWidget, TinyMCEWidget


class CreateEmailTemplatesForm(IndicoForm):
    title = StringField(_("Title"), [DataRequired(), Length(max=100)])
    subject = StringField(_("Subject"), [DataRequired(), Length(max=75)])
    body = TextAreaField(_("Email body"), [DataRequired(), NoRelativeURLs()],
                            widget=TinyMCEWidget(absolute_urls=True, images=True))
    is_cloneable = BooleanField(_('Allow cloning'), widget=SwitchWidget(), default=True,
                                description=_('Allow cloning this template in subcategories and events'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.content.description = (render_placeholder_info('registration-email',
                                                            regform=self.regform, registration=None))
