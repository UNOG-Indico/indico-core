# This file is part of Indico.
# Copyright (C) 2002 - 2024 CERN
#
# Indico is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see the
# LICENSE file for more details.

from datetime import datetime

from celery.schedules import crontab

from indico.core.celery import celery
from indico.core.db import db
from indico.web.flask.models import UserSession


@celery.periodic_task(name='delete_stored_user_sessions', run_every=crontab(minute='0'))
def delete_user_sessions():
    """Delete expired user sessions from postgres."""
    UserSession.query.filter(UserSession.ttl < datetime.now()).delete()
    db.session.commit()
