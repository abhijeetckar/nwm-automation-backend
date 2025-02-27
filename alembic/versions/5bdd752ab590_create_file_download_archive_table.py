"""create file download archive table

Revision ID: 5bdd752ab590
Revises: e699b16c05f3
Create Date: 2025-02-27 10:12:22.308265

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5bdd752ab590'
down_revision: Union[str, None] = 'e699b16c05f3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        'file_download_archive',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('date', sa.DateTime, nullable=False),
        sa.Column('log', sa.dialects.postgresql.JSONB)

    )

def downgrade():
    op.drop_table('file_download_archive')
