"""add usingmethod and composition field to product model

Revision ID: a999c9fe7b01
Revises: c5dd116e98be
Create Date: 2025-04-03 16:54:27.691704

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a999c9fe7b01"
down_revision: Union[str, None] = "c5dd116e98be"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "products", sa.Column("usingmethod", sa.Text(), nullable=True)
    )
    op.add_column(
        "products", sa.Column("composition", sa.Text(), nullable=True)
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("products", "composition")
    op.drop_column("products", "usingmethod")
    # ### end Alembic commands ###
