"""add brand, group and category tables

Revision ID: 06a240ab25eb
Revises: efd81cd6c2fe
Create Date: 2024-07-26 20:47:49.451033

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "06a240ab25eb"
down_revision: Union[str, None] = "efd81cd6c2fe"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "brands",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("image_url", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_brands")),
    )
    op.create_table(
        "groups",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("image_url", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_groups")),
    )
    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("group_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["group_id"],
            ["groups.id"],
            name=op.f("fk_categories_group_id_groups"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_categories")),
    )
    op.create_table(
        "category_properties",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["category_id"],
            ["categories.id"],
            name=op.f("fk_category_properties_category_id_categories"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_category_properties")),
    )
    op.create_table(
        "values",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("value", sa.String(), nullable=False),
        sa.Column("category_property_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["category_property_id"],
            ["category_properties.id"],
            name=op.f("fk_values_category_property_id_category_properties"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_values")),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("values")
    op.drop_table("category_properties")
    op.drop_table("categories")
    op.drop_table("groups")
    op.drop_table("brands")
    # ### end Alembic commands ###
