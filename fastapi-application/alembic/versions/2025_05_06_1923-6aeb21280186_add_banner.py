"""Add banner

Revision ID: 6aeb21280186
Revises: e5e2f5c6bab0
Create Date: 2025-05-06 19:23:38.251717

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "6aeb21280186"
down_revision: Union[str, None] = "e5e2f5c6bab0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("banners", sa.Column("status", sa.Boolean(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("banners", "status")
    # ### end Alembic commands ###
