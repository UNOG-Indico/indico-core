"""Add regform templates at category

Revision ID: 64673b9d6ae2
Revises: b4ee48f3052c
Create Date: 2025-08-12 11:09:51.324985
"""

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = '64673b9d6ae2'
down_revision = 'b4ee48f3052c'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('forms', sa.Column('category_id', sa.Integer(), nullable=True), schema='event_registration')
    op.add_column('forms', sa.Column('cloned_from_id', sa.Integer(), nullable=True), schema='event_registration')
    op.create_foreign_key(None, 'forms', 'categories', ['category_id'], ['id'],
                          source_schema='event_registration', referent_schema='categories')
    op.create_check_constraint('event_xor_category_id_null', 'forms', '(event_id IS NULL) != (category_id IS NULL)',
                               schema='event_registration')
    op.alter_column('forms', 'event_id', existing_type=sa.Integer(), nullable=True, schema='event_registration')


def downgrade():
    op.drop_constraint('ck_forms_event_xor_category_id_null', 'forms', schema='event_registration')
    op.drop_column('forms', 'category_id', schema='event_registration')
    op.drop_column('forms', 'cloned_from_id', schema='event_registration')
    op.alter_column('forms', 'event_id', existing_type=sa.Integer(), nullable=False, schema='event_registration')
