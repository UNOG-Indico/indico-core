# This file is part of Indico.
# Copyright (C) 2002 - 2025 CERN
#
# Indico is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see the
# LICENSE file for more details.

from sqlalchemy import DDL, Index, text
from sqlalchemy.event import listens_for
from sqlalchemy.sql import func
from sqlalchemy.sql.elements import conv


# if you wonder why search_path is set and the two-argument `unaccent` function is used,
# see this post on stackoverflow: http://stackoverflow.com/a/11007216/298479
SQL_FUNCTION_UNACCENT = '''
    CREATE FUNCTION indico.indico_unaccent(value TEXT)
        RETURNS TEXT
    AS $$
    BEGIN
        RETURN unaccent('unaccent', value);
    END;
    $$
    LANGUAGE plpgsql IMMUTABLE SET search_path = public, pg_temp;
'''


def _should_create_function(ddl, target, connection, **kw):
    sql = "SELECT COUNT(*) FROM information_schema.routines WHERE routine_name = 'indico_unaccent'"
    count = connection.execute(text(sql)).scalar()
    return not count


def create_unaccent_function(conn):
    """Create the unaccent function if it doesn't exist yet."""
    DDL(SQL_FUNCTION_UNACCENT).execute_if(callable_=_should_create_function).execute(conn)


def define_unaccented_lowercase_index(column, table=None, custom_name=None):
    """Define an index that uses the indico_unaccent function.

    Since this is usually used for searching, the column's value is
    also converted to lowercase before being unaccented. To make proper
    use of this index, use this criterion when querying the table::

        db.func.indico.indico_unaccent(db.func.lower(column)).ilike(...)

    The index will use the trgm operators which allow very efficient LIKE
    even when searching e.g. ``LIKE '%something%'``.

    :param column: The column the index should be created on, e.g.
                   ``User.first_name``
    :param table: The table in case the column is a column property
    :param custom_name: The name of the index, in case the column is
                         a column property
    """
    if table is None:
        table = column.table

    @listens_for(table, 'after_create')
    def _after_create(target, conn, **kw):
        assert target is table
        col_func = func.indico.indico_unaccent(func.lower(column))
        index_kwargs = {'postgresql_using': 'gin',
                        'postgresql_ops': {col_func.key: 'gin_trgm_ops'}}
        index_name = custom_name or f'ix_{column.table.name}_{column.name}_unaccent'
        Index(conv(index_name), col_func, **index_kwargs).create(conn)


def unaccent_match(column, value, exact):
    from indico.core.db import db
    value = value.replace('%', r'\%').replace('_', r'\_').lower()
    if not exact:
        value = f'%{value}%'
    # we always use LIKE, even for an exact match. when using the pg_trgm indexes this is
    # actually faster than `=`
    return db.func.indico.indico_unaccent(db.func.lower(column)).ilike(db.func.indico.indico_unaccent(value))
