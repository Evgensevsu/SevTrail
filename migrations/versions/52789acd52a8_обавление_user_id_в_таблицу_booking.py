"""Добавление user_id в таблицу booking

Revision ID: 52789acd52a8
Revises: 5cb7592837f3
Create Date: 2024-12-12 12:25:57.918343
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '52789acd52a8'
down_revision = '5cb7592837f3'
branch_labels = None
depends_on = None


def upgrade():
    # ### команды для изменения таблицы ###
    with op.batch_alter_table('booking', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column('booking_date', sa.Date(), nullable=False))
        batch_op.create_foreign_key('fk_booking_user', 'user', ['user_id'], ['id'])
        batch_op.drop_column('comment')
        batch_op.drop_column('user_name')
        batch_op.drop_column('date')
    # ### end Alembic commands ###


def downgrade():
    # ### откат изменений ###
    with op.batch_alter_table('booking', schema=None) as batch_op:
        batch_op.add_column(sa.Column('date', sa.DATE(), nullable=False))
        batch_op.add_column(sa.Column('user_name', sa.VARCHAR(length=100), nullable=False))
        batch_op.add_column(sa.Column('comment', sa.TEXT(), nullable=True))
        batch_op.drop_constraint('fk_booking_user', type_='foreignkey')
        batch_op.drop_column('booking_date')
        batch_op.drop_column('user_id')
    # ### end Alembic commands ###
