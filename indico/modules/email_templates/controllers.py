# This file is part of Indico.
# Copyright (C) 2002 - 2025 CERN
#
# Indico is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see the
# LICENSE file for more details.

from flask import flash, request, session
from werkzeug.exceptions import Forbidden, NotFound

from indico.core.db import db
from indico.modules.categories.controllers.base import RHManageCategoryBase
from indico.modules.email_templates.forms import CreateEmailTemplatesForm
from indico.modules.email_templates.models.email_templates import EmailTemplate
from indico.modules.email_templates.util import get_inherited_templates
from indico.modules.email_templates.views import WPCategoryManagementEmailTemplate, WPEventManagementEmailTemplate
from indico.modules.events import Event
from indico.modules.events.management.controllers import RHManageEventBase
from indico.modules.events.util import check_event_locked
from indico.util.i18n import _
from indico.util.placeholders import get_placeholders
from indico.web.flask.templating import get_template_module
from indico.web.rh import RHProtected
from indico.web.util import jsonify_data, jsonify_form


def _render_template_list(target, event=None):
    tpl = get_template_module('email_template/_list.html')
    return tpl.render_template_list(target.email_templates, target, event=event,
                                    inherited_templates=get_inherited_templates(target))


class TemplateDesignerMixin:
    """Basic class for all template designer mixins.

    It resolves the target object type from the blueprint URL.
    """

    @property
    def object_type(self):
        """Figure out whether we're targeting an event or category, based on URL info."""
        return request.view_args['object_type']

    @property
    def event_or_none(self):
        return self.target if self.object_type == 'event' else None

    def _render_template(self, tpl_name, **kwargs):
        view_class = (WPEventManagementEmailTemplate
                      if self.object_type == 'event' else WPCategoryManagementEmailTemplate)
        return view_class.render_template(tpl_name, self.target, 'email_templates',
                                          target=self.target, **kwargs)


class SpecificTemplateMixin(TemplateDesignerMixin):
    """Mixin that accepts a target template passed in the URL.

    The target category/event will be the owner of that template.
    """

    normalize_url_spec = {
        'locators': {
            lambda self: self.email_tpl
        }
    }

    @property
    def target(self):
        return self.email_tpl.owner

    def _check_access(self):
        self._require_user()
        if not self.target.can_manage(session.user):
            raise Forbidden
        elif isinstance(self.target, Event):
            check_event_locked(self, self.target)

    def _process_args(self):
        self.email_tpl = EmailTemplate.get_or_404(request.view_args['email_template_id'])
        if self.target.is_deleted:
            raise NotFound


class TargetFromURLMixin(TemplateDesignerMixin):
    """Mixin that takes the target event/category from the URL that is passed."""

    @property
    def target_dict(self):
        return {'event': self.event} if self.object_type == 'event' else {'category': self.category}

    @property
    def target(self):
        return self.event if self.object_type == 'event' else self.category


class TemplateListMixin(TargetFromURLMixin):
    def _process(self):
        templates = get_inherited_templates(self.target)
        return self._render_template('list.html', inherited_templates=templates)


class AddTemplateMixin(TargetFromURLMixin):
    always_cloneable = False

    def _check_access(self):
        if not self.target.can_manage(session.user):
            raise Forbidden

    def _process(self):
        form = CreateEmailTemplatesForm()
        if self.always_clonable:
            del form.is_cloneable
        if form.validate_on_submit():
            is_clonable = form.is_cloneable.data if form.is_cloneable else True
            type = 'Registration'
            new_email_template = EmailTemplate(title=form.title.data, type=type, is_clonable=is_clonable,
                                         **self.target_dict)
            flash(_("Added new email template '{}'").format(new_email_template.title), 'success')
            return jsonify_data(html=_render_template_list(self.target, event=self.event_or_none))
        return jsonify_form(form, disabled_until_change=False)



class RHListEventEmailTemplates(TemplateListMixin, RHManageEventBase):
    pass


class RHListCategoryEmailTemplates(TemplateListMixin, RHManageCategoryBase):
    pass


class RHAddEventEmailTemplate(AddTemplateMixin, RHManageEventBase):
    always_cloneable = True


class RHAddCategoryEmailTemplate(AddTemplateMixin, RHManageCategoryBase):
    always_cloneable = True


class RHModifyEmailTemplateBase(SpecificTemplateMixin, RHProtected):
    def _check_access(self):
        RHProtected._check_access(self)
        SpecificTemplateMixin._check_access(self)


class RHEditEmailTemplate(RHModifyEmailTemplateBase):
    def _process(self):
        placeholders = get_placeholders('registration-email', regform=None, registration=None)
        return self._render_template('template.html', template=self.email_tpl,
                                     placeholders=placeholders, owner=self.target)


class RHDeleteEmailTemplate(RHModifyEmailTemplateBase):
    def _process(self):
        db.session.delete(self.email_tpl)
        db.session.flush()
        flash(_('The email template has been deleted'), 'success')
        return jsonify_data(html=_render_template_list(self.target, event=self.event_or_none))
