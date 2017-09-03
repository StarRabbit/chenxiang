"""empty message

Revision ID: a732ba7913f8
Revises: a3514e2454b9
Create Date: 2017-05-19 18:32:45.504842

"""

# revision identifiers, used by Alembic.
revision = 'a732ba7913f8'
down_revision = 'a3514e2454b9'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('reviews', sa.Column('author_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'reviews', 'users', ['author_id'], ['id'])
    op.drop_column('reviews', 'author_name')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('reviews', sa.Column('author_name', mysql.VARCHAR(length=64), nullable=True))
    op.drop_constraint(None, 'reviews', type_='foreignkey')
    op.drop_column('reviews', 'author_id')
    ### end Alembic commands ###