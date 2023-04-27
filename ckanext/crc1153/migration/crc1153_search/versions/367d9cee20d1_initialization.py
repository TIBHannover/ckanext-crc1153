"""initialization

Revision ID: 367d9cee20d1
Revises: 
Create Date: 2023-04-27 10:39:34.335760

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '367d9cee20d1'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'crc1153_data_resource_column_index',
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('resource_id', sa.UnicodeText(), sa.ForeignKey('resource.id'), nullable=False),
        sa.Column('columns_names', sa.UnicodeText(), nullable=False)
    )


def downgrade():
    op.drop_table('crc1153_data_resource_column_index')
