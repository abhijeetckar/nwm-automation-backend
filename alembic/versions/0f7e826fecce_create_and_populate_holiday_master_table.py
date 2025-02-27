"""create and populate holiday master table

Revision ID: 0f7e826fecce
Revises: 
Create Date: 2025-02-27 09:59:22.128416

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0f7e826fecce'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        'holiday_master',
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

    holiday_master = sa.table(
        "holiday_master",
        sa.Column("date", sa.Date),
        sa.Column("day", sa.String(50)),
        sa.Column("defer_all", sa.Boolean),
        sa.Column("description", sa.String(50)),
        sa.Column("allow_download", sa.dialects.postgresql.JSONB),
    )

    op.bulk_insert(
        holiday_master,
        [
            {"date": "2025-02-19", "day": "Wednesday", "defer_all": True, "description": "Chhatrapati Shivaji Maharaj Jayanti"},
            {"date": "2025-02-26", "day": "Wednesday", "defer_all": True, "description": "Mahashivratri"},
            {"date": "2025-03-14", "day": "Friday", "defer_all": True, "description": "Holi"},
            {"date": "2025-03-31", "day": "Monday", "defer_all": True, "description": "Id-Ul-Fitr (Ramadan Eid)"},
            {"date": "2025-04-01", "day": "Tuesday", "defer_all": True, "description": "Annual Bank closing"},
            {"date": "2025-04-10", "day": "Thursday", "defer_all": True, "description": "Shri Mahavir Jayanti"},
            {"date": "2025-04-14", "day": "Monday", "defer_all": True, "description": "Dr. Baba Saheb Ambedkar Jayanti"},
            {"date": "2025-04-18", "day": "Friday", "defer_all": True, "description": "Good Friday"},
            {"date": "2025-05-01", "day": "Thursday", "defer_all": True, "description": "Maharashtra Day"},
            {"date": "2025-05-12", "day": "Monday", "defer_all": True, "description": "Buddha Pournima"},
            {"date": "2025-08-15", "day": "Friday", "defer_all": True, "description": "Independence Day / Parsi New Year"},
            {"date": "2025-08-27", "day": "Wednesday", "defer_all": True, "description": "Shri Ganesh Chaturthi"},
            {"date": "2025-09-05", "day": "Friday", "defer_all": True, "description": "Id-E-Milad"},
            {"date": "2025-10-02", "day": "Thursday", "defer_all": True, "description": "Mahatma Gandhi Jayanti/Dussehra"},
            {"date": "2025-10-21", "day": "Tuesday", "defer_all": True, "description": "Diwali Laxmi Pujan"},
            {"date": "2025-10-22", "day": "Wednesday", "defer_all": True, "description": "Balipratipada"},
            {"date": "2025-11-05", "day": "Wednesday", "defer_all": True, "description": "Prakash Gurpurb Sri Guru Nanak Dev"},
            {"date": "2025-12-25", "day": "Thursday", "defer_all": True, "description": "Christmas"},
        ],
    )


def downgrade():
    op.drop_table('holiday_master')