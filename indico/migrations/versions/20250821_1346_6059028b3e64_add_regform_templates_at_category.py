"""Add regform templates at category

Revision ID: 6059028b3e64
Revises: 6fac01c501b6
Create Date: 2025-08-21 13:46:04.399634
"""

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = '6059028b3e64'
down_revision = '6fac01c501b6'
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
    op.execute('''
        CREATE OR REPLACE FUNCTION disallow_registration_on_forms_linked_to_categories()
        RETURNS trigger AS $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM event_registration.forms rf
                WHERE rf.id = NEW.registration_form_id
                AND rf.category_id IS NOT NULL
            ) THEN
                RAISE EXCEPTION 'Registrations cannot be linked to template forms associated with a category';
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        CREATE TRIGGER registrations_prevent_forms_linked_to_categories
        BEFORE INSERT OR UPDATE ON event_registration.registrations
        FOR EACH ROW
        EXECUTE FUNCTION disallow_registration_on_forms_linked_to_categories();
    ''')
    op.drop_constraint('ck_logs_valid_enum_realm', 'logs', schema='categories')
    op.create_check_constraint('valid_enum_realm', 'logs', '(realm = ANY (ARRAY[1, 2, 3]))', schema='categories')


def downgrade():
    op.execute('DROP TRIGGER IF EXISTS registrations_prevent_forms_linked_to_categories ON event_registration.registrations;')
    op.execute('DROP FUNCTION IF EXISTS disallow_registration_on_forms_linked_to_categories;')
    op.execute('''DELETE FROM event_registration.forms WHERE category_id IS NOT NULL; ''')  # I thought there was cascading delete between registration form and the form fields?
    op.drop_constraint('ck_forms_event_xor_category_id_null', 'forms', schema='event_registration')
    op.drop_column('forms', 'category_id', schema='event_registration')
    op.drop_column('forms', 'cloned_from_id', schema='event_registration')
    op.alter_column('forms', 'event_id', existing_type=sa.Integer(), nullable=False, schema='event_registration')
    op.drop_constraint('ck_logs_valid_enum_realm', 'logs', schema='categories')
    op.create_check_constraint('valid_enum_realm', 'logs', '(realm = ANY (ARRAY[1, 2]))', schema='categories')
