"""create file download log table

Revision ID: e699b16c05f3
Revises: 345a4acf3505
Create Date: 2025-02-27 10:10:34.942128

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from app.models.files_master import file_time_enum

# revision identifiers, used by Alembic.
revision: str = 'e699b16c05f3'
down_revision: Union[str, None] = '345a4acf3505'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        'file_download_log',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('filename', sa.String(50), nullable=False),
        sa.Column('fileurl', sa.String(255), nullable=False),
        sa.Column('downloaded', sa.Boolean),
        sa.Column('reason', sa.String(50)),
        sa.Column('attempts', sa.Integer),
        sa.Column('downloaded_at', sa.DateTime),
        sa.Column('is_private', sa.Boolean, nullable=False, server_default=sa.text("FALSE")),  # Corrected default
        sa.Column('source', sa.String(50), nullable=True),  # Should be nullable for constraint logic
        sa.Column("file_time", file_time_enum, nullable=False, server_default="EOD"),
        sa.CheckConstraint(
            "NOT is_private OR source IS NOT NULL",  # Corrected check constraint
            name="check_private_source_not_null"
        )
    )

def downgrade():
    op.drop_table('file_download_log')
    file_time_enum.drop(op.get_bind(), checkfirst=True)