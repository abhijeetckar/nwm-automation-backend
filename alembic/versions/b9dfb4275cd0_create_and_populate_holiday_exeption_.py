"""create and populate holiday exeption table

Revision ID: b9dfb4275cd0
Revises: 0f7e826fecce
Create Date: 2025-02-27 10:03:47.057217

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b9dfb4275cd0'
down_revision: Union[str, None] = '0f7e826fecce'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        'holiday_exception',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('date', sa.Date, nullable=False),
        sa.Column('day', sa.String(50), nullable=False),
        sa.Column("defer_all", sa.Boolean, default=True, nullable=False),
        sa.Column('description', sa.String(50)),
        sa.Column("allow_download", sa.dialects.postgresql.JSONB, nullable=True, server_default="[]"),
        sa.CheckConstraint(
            "defer_all = TRUE OR (allow_download IS NOT NULL AND jsonb_array_length(allow_download) > 0)",
            name="check_allow_download_not_empty_if_defer_all_false"
        )
    )


    holiday_exception = sa.table(
        "holiday_exception",
        sa.Column("date", sa.Date),
        sa.Column("day", sa.String(50)),
        sa.Column("defer_all", sa.Boolean),
        sa.Column("description", sa.String(50)),
        sa.Column("allow_download", sa.dialects.postgresql.JSONB),
    )

    op.bulk_insert(
        holiday_exception,
        [
            {"date": "2025-10-21", "day": "Tuesday", "defer_all": True, "description": "Diwali Laxmi Pujan Muhurat Trading"},
        ],
    )

def downgrade():
    op.drop_table('holiday_exception')