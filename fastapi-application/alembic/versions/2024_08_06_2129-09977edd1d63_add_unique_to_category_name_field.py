"""add unique to category name field

Revision ID: 09977edd1d63
Revises: adbfdaabf588
Create Date: 2024-08-06 21:29:04.500424

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "09977edd1d63"
down_revision: Union[str, None] = "adbfdaabf588"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(
        op.f("uq_categories_name"), "categories", ["name"]
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(
        op.f("uq_categories_name"), "categories", type_="unique"
    )
    # ### end Alembic commands ###