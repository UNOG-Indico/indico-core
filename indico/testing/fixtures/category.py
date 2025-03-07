# This file is part of Indico.
# Copyright (C) 2002 - 2025 CERN
#
# Indico is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see the
# LICENSE file for more details.

import pytest

from indico.modules.categories import Category


@pytest.fixture
def create_category(db):
    """Return a callable which lets you create dummy events."""

    def _create_category(id_=None, **kwargs):
        kwargs.setdefault('title', f'cat#{id_}' if id_ is not None else 'dummy')
        kwargs.setdefault('timezone', 'UTC')
        if 'parent' not in kwargs:
            kwargs['parent'] = Category.get_root()
        category = Category(id=id_, acl_entries=set(), **kwargs)
        db.session.add(category)
        db.session.flush()
        return category

    return _create_category


@pytest.fixture
def dummy_category(create_category):
    """Create a mocked dummy category."""
    return create_category(title='dummy', id_=42)
