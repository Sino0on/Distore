"""merge heads

Revision ID: 27fa42177b38
Revises: a698c2417cab, 2dd6710fa44e
Create Date: 2025-04-22 18:23:05.650221

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "27fa42177b38"
down_revision: Union[str, None] = ("a698c2417cab", "2dd6710fa44e")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
