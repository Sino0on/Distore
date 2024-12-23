"""add uuid_1c field to category model

Revision ID: 51ecb79819c6
Revises: 312ab4303c6e
Create Date: 2024-09-18 19:28:25.533686

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "51ecb79819c6"
down_revision: Union[str, None] = "312ab4303c6e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "categories", sa.Column("uuid_1c", sa.String(), nullable=True)
    )
    op.create_unique_constraint(
        op.f("uq_categories_uuid_1c"), "categories", ["uuid_1c"]
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(
        op.f("uq_categories_uuid_1c"), "categories", type_="unique"
    )
    op.drop_column("categories", "uuid_1c")
    # ### end Alembic commands ###