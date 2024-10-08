"""added table testModel

Revision ID: 7cca0520324e
Revises: 9af5ec3df58f
Create Date: 2024-08-20 15:17:08.982706

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7cca0520324e'
down_revision = '9af5ec3df58f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('test_model',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('text_test', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('test_model')
    # ### end Alembic commands ###
