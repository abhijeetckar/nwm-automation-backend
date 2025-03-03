"""create and populate files master table

Revision ID: 345a4acf3505
Revises: b9dfb4275cd0
Create Date: 2025-02-27 10:06:06.527242

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '345a4acf3505'
down_revision: Union[str, None] = 'b9dfb4275cd0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        'files_master',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('filename', sa.String(150), nullable=False),
        sa.Column('url', sa.String(150), nullable=False),
        sa.Column('is_private', sa.Boolean, nullable=False, server_default=sa.text("FALSE")),  # Corrected default
        sa.Column('source', sa.String(50), nullable=True),  # Should be nullable for constraint logic
        sa.CheckConstraint(
            "NOT is_private OR source IS NOT NULL",  # Corrected check constraint
            name="check_private_source_not_null"
        )
    )

    # Define table reference for bulk insert
    files_master = sa.table(
        "files_master",
        sa.column("filename", sa.String),
        sa.column("url", sa.String),
        sa.column("is_private", sa.Boolean),
        sa.column("source", sa.String),
    )

    # Perform bulk insert
    op.bulk_insert(
        files_master,
        [
            {"filename": "BhavCopy_NSE_CM_0_0_0_YYYYMMDD_F_0000.csv.zip", "url": "https://nsearchives.nseindia.com/content/cm/", "is_private": False, "source": None},
            {"filename": "MF_VAR_DDMMYYYY.csv", "url": "https://nsearchives.nseindia.com/archives/equities/mf_haircut/", "is_private": False, "source": None},
            {"filename": "C_VAR1_DDMMYYYY_6.DAT", "url": "https://nsearchives.nseindia.com/archives/nsccl/var/", "is_private": False, "source": None},
            {"filename": "C_VAR1_DDMMYYYY_1.DAT", "url": "https://nsearchives.nseindia.com/archives/nsccl/var/", "is_private": False, "source": None},
            {"filename": "BhavCopy_BSE_CM_0_0_0_YYYYMMDD_F_0000.csv", "url": "https://www.bseindia.com/download/BhavCopy/Equity/", "is_private": False, "source": None},

            # Corrected `is_private` to use `True` instead of `sa.true()`
            {"filename": "C_90296_SEC_PLEDGE_DDMMYYYY_01.csv.gz", "url": "https://www.connect2nse.com/extranet-api/member/file/download/2.0?segment=CM&folderPath=/Reports&filename=", "is_private": True, "source": "NSCCL"},
            {"filename": "F_90296_SEC_PLEDGE_DDMMYYYY_01.csv.gz", "url": "https://www.connect2nse.com/extranet-api/member/file/download/2.0?segment=FO&folderPath=/Reports&filename=", "is_private": True, "source": "NSCCL"},
            {"filename": "C_90296_SEC_PLEDGE_DDMMYYYY_02.csv.gz", "url": "https://www.connect2nse.com/extranet-api/member/file/download/2.0?segment=CM&folderPath=/Reports&filename=", "is_private": True, "source": "NSCCL"},
            {"filename": "F_90296_SEC_PLEDGE_DDMMYYYY_02.csv.gz", "url": "https://www.connect2nse.com/extranet-api/member/file/download/2.0?segment=FO&folderPath=/Reports&filename=", "is_private": True, "source": "NSCCL"},
            {"filename": "Position_NCL_FO_0_CM_90296_YYYYMMDD_F_0000.csv.gz", "url": "https://www.connect2nse.com/extranet-api/member/file/download/2.0?segment=FO&folderPath=/Reports&filename=", "is_private": True, "source": "NSCCL"},
        ],
    )


def downgrade():
    op.drop_table('files_master')