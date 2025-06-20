"""add parent product to CartProduct model

Revision ID: 3982cf74a41c
Revises: affce0bf55c8
Create Date: 2025-06-20 19:32:56.185597

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "3982cf74a41c"
down_revision: Union[str, None] = "affce0bf55c8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###

    op.add_column(
        "cart_products",
        sa.Column("parent_cart_product_id", sa.Integer(), nullable=True),
    )
    op.drop_constraint(
        "fk_cart_products_parent_product_id_cart_products",
        "cart_products",
        type_="foreignkey",
    )
    op.create_foreign_key(
        op.f("fk_cart_products_parent_cart_product_id_cart_products"),
        "cart_products",
        "cart_products",
        ["parent_cart_product_id"],
        ["id"],
    )
    op.drop_column("cart_products", "parent_product_id")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "cart_products",
        sa.Column(
            "parent_product_id",
            sa.INTEGER(),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.drop_constraint(
        op.f("fk_cart_products_parent_cart_product_id_cart_products"),
        "cart_products",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "fk_cart_products_parent_product_id_cart_products",
        "cart_products",
        "cart_products",
        ["parent_product_id"],
        ["id"],
    )
    op.drop_column("cart_products", "parent_cart_product_id")

    # ### end Alembic commands ###
