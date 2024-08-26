"""init migration

Revision ID: 9af5ec3df58f
Revises: 
Create Date: 2024-08-20 15:13:07.060523

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '9af5ec3df58f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('kombu_message', schema=None) as batch_op:
        batch_op.drop_index('ix_kombu_message_timestamp')
        batch_op.drop_index('ix_kombu_message_timestamp_id')
        batch_op.drop_index('ix_kombu_message_visible')

    op.drop_table('kombu_message')
    op.drop_table('kombu_queue')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('kombu_queue',
    sa.Column('id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('name', sa.VARCHAR(length=200), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='kombu_queue_pkey'),
    sa.UniqueConstraint('name', name='kombu_queue_name_key'),
    postgresql_ignore_search_path=False
    )
    op.create_table('kombu_message',
    sa.Column('id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('visible', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('timestamp', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('payload', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('version', sa.SMALLINT(), autoincrement=False, nullable=False),
    sa.Column('queue_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['queue_id'], ['kombu_queue.id'], name='FK_kombu_message_queue'),
    sa.PrimaryKeyConstraint('id', name='kombu_message_pkey')
    )
    with op.batch_alter_table('kombu_message', schema=None) as batch_op:
        batch_op.create_index('ix_kombu_message_visible', ['visible'], unique=False)
        batch_op.create_index('ix_kombu_message_timestamp_id', ['timestamp', 'id'], unique=False)
        batch_op.create_index('ix_kombu_message_timestamp', ['timestamp'], unique=False)

    # ### end Alembic commands ###
