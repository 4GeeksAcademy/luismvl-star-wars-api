"""empty message

Revision ID: eb2feccbcbfc
Revises: 7edac7d03ae7
Create Date: 2023-07-17 20:48:29.830371

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'eb2feccbcbfc'
down_revision = '7edac7d03ae7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('planets', schema=None) as batch_op:
        batch_op.add_column(sa.Column('orbital_period', sa.Integer(), nullable=True))
        batch_op.alter_column('rotation_period',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('population',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('surface_water',
               existing_type=sa.INTEGER(),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('planets', schema=None) as batch_op:
        batch_op.alter_column('surface_water',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('population',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('rotation_period',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.drop_column('orbital_period')

    # ### end Alembic commands ###
