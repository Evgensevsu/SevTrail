"""Initial migration

Revision ID: cdb1294e3c2b
Revises: 
Create Date: 2024-12-12 10:58:34.629229

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cdb1294e3c2b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('route',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('length', sa.Float(), nullable=False),
    sa.Column('difficulty', sa.String(length=50), nullable=False),
    sa.Column('start_point', sa.String(length=100), nullable=False),
    sa.Column('end_point', sa.String(length=100), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('id',
               existing_type=sa.INTEGER(),
               nullable=False,
               autoincrement=True)
        batch_op.alter_column('username',
               existing_type=sa.TEXT(),
               type_=sa.String(length=120),
               existing_nullable=False)
        batch_op.alter_column('password',
               existing_type=sa.TEXT(),
               type_=sa.String(length=120),
               existing_nullable=False)
        batch_op.alter_column('role',
               existing_type=sa.TEXT(),
               type_=sa.String(length=50),
               existing_nullable=True,
               existing_server_default=sa.text("'user'"))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('role',
               existing_type=sa.String(length=50),
               type_=sa.TEXT(),
               existing_nullable=True,
               existing_server_default=sa.text("'user'"))
        batch_op.alter_column('password',
               existing_type=sa.String(length=120),
               type_=sa.TEXT(),
               existing_nullable=False)
        batch_op.alter_column('username',
               existing_type=sa.String(length=120),
               type_=sa.TEXT(),
               existing_nullable=False)
        batch_op.alter_column('id',
               existing_type=sa.INTEGER(),
               nullable=True,
               autoincrement=True)

    op.drop_table('route')
    # ### end Alembic commands ###