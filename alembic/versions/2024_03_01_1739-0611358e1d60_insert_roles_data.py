"""insert roles data

Revision ID: 0611358e1d60
Revises: 01
Create Date: 2024-03-01 17:39:44.344449

"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy import table, column, String, Integer, UUID

from src.core.constants import DEFAULT_ROLE_DATA, SUPERUSER_ROLE_DATA

# revision identifiers, used by Alembic.
revision: str = '0611358e1d60'
down_revision: Union[str, None] = '01'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    roles_table = table('role',
        column('id', UUID),
        column('name', String),
        column('access_level', Integer),
    )
    op.bulk_insert(
        table=roles_table,
        rows=[
            {'id': '0eb8b11e-7a2a-421f-a792-6bab5cc9211a', **DEFAULT_ROLE_DATA},
            {'id': '7c58fbfd-d77a-4ffa-8245-60e279ffe6b0', **SUPERUSER_ROLE_DATA}
        ]
    )


def downgrade() -> None:
    op.execute("DELETE FROM role WHERE name IN ('user', 'superuser');")
