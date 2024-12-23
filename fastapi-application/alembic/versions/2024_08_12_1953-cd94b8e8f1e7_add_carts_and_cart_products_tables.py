"""add carts and cart products tables

Revision ID: cd94b8e8f1e7
Revises: 39568c7a009f
Create Date: 2024-08-12 19:53:16.000673

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "cd94b8e8f1e7"
down_revision: Union[str, None] = "39568c7a009f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "carts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("total_price", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_carts_user_id_users")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_carts")),
    )
    op.create_table(
        "cart_products",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("cart_id", sa.Integer(), nullable=False),
        sa.Column("product_variation_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["cart_id"],
            ["carts.id"],
            name=op.f("fk_cart_products_cart_id_carts"),
        ),
        sa.ForeignKeyConstraint(
            ["product_variation_id"],
            ["product_variations.id"],
            name=op.f(
                "fk_cart_products_product_variation_id_product_variations"
            ),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_cart_products")),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("cart_products")
    op.drop_table("carts")
    # ### end Alembic commands ###