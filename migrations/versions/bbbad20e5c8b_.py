"""empty message

Revision ID: bbbad20e5c8b
Revises: 065f49ccefff
Create Date: 2023-07-11 02:01:19.178104

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bbbad20e5c8b'
down_revision = '065f49ccefff'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('characters', schema=None) as batch_op:
        batch_op.alter_column('birth_year',
               existing_type=sa.DATE(),
               type_=sa.String(length=250),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('characters', schema=None) as batch_op:
        batch_op.alter_column('birth_year',
               existing_type=sa.String(length=250),
               type_=sa.DATE(),
               existing_nullable=True)

    # ### end Alembic commands ###
