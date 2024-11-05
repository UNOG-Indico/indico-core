"""move_user_sessions_to_postgres

Revision ID: fb255305ea83
Revises: 75db3a4a4ed4
Create Date: 2024-10-23 15:17:02.490888
"""

import pickle
from datetime import datetime

import sqlalchemy as sa
from alembic import op

from indico.core.cache import make_scoped_cache


# revision identifiers, used by Alembic.
revision = 'fb255305ea83'
down_revision = '34f27622213b'
branch_labels = None
depends_on = None

debug = True  # TODO Set this as False when ready to permanently move sessions associated to a user from redis to postgres
serilizer = pickle


def upgrade():
    op.create_table(
        'user_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('sid', sa.String(), nullable=False, unique=True),
        sa.Column('data', sa.LargeBinary(), nullable=False),
        sa.Column('ttl', sa.DateTime(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.users.id']),
        schema='indico'
    )
    conn = op.get_bind()
    storage = make_scoped_cache('flask-session')
    session_sids = storage.cache.cache._write_client.keys('indico_v3.3_flask-session/*')
    session_sids = (x.decode('utf-8') for x in session_sids)
    session_sids = (x.replace('indico_v3.3_flask-session/', '') for x in session_sids)
    for sid in session_sids:
        try:
            session_data = storage.get(sid)
            data = serilizer.loads(session_data)
            if data.get('_user_id'):
                conn.execute('''
                    INSERT INTO indico.user_sessions
                    (sid, data, ttl, user_id) VALUES
                    (%s,       %s,      %s,    %s);
                    ''', (sid, serilizer.dumps(dict(data)), data['_expires'], data['_user_id'])
                )
                if not debug:
                    storage.delete(sid)
        except TypeError as e:
            print(f'Something wrong upgrading sid {sid}: {e}')


def downgrade():
    if not debug:  # The upgrade script does not delete the records from redis when in debug so no need to return them here
        storage = make_scoped_cache('flask-session')
        conn = op.get_bind()
        user_sessions = conn.execute('''SELECT * FROM indico.user_sessions;''')
        for session in user_sessions:
            storage_ttl = session.ttl - datetime.now()
            if storage_ttl.total_seconds() <= 0:  # Do not save expired sessions
                continue
            try:
                data = serilizer.loads(session.data)
                storage.set(session.sid, serilizer.dumps(dict(data)), storage_ttl)
            except TypeError as e:
                print(f'Something wrong downgrading sid {session.sid}: {e}')
    op.drop_table('user_sessions', schema='indico')
