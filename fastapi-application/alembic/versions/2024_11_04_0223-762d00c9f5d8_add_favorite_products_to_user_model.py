"""add favorite products to user model

Revision ID: 762d00c9f5d8
Revises: 2b809996e00a
Create Date: 2024-11-04 02:23:05.197392

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "762d00c9f5d8"
down_revision: Union[str, None] = "2b809996e00a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "user_favorites",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
            name=op.f("fk_user_favorites_product_id_products"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_user_favorites_user_id_users"),
        ),
        sa.PrimaryKeyConstraint(
            "user_id", "product_id", name=op.f("pk_user_favorites")
        ),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("user_favorites")
    # ### end Alembic commands ###
