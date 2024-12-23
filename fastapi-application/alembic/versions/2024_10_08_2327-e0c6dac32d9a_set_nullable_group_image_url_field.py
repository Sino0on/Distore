"""set nullable group image_url field

Revision ID: e0c6dac32d9a
Revises: 0d259e0c14a8
Create Date: 2024-10-08 23:27:18.522341

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e0c6dac32d9a"
down_revision: Union[str, None] = "0d259e0c14a8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "category_properties",
        sa.Column("uuid_1c", sa.String(), nullable=False),
    )
    op.create_unique_constraint(
        op.f("uq_category_properties_uuid_1c"),
        "category_properties",
        ["uuid_1c"],
    )
    op.alter_column(
        "groups", "image_url", existing_type=sa.VARCHAR(), nullable=True
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "groups", "image_url", existing_type=sa.VARCHAR(), nullable=False
    )
    op.drop_constraint(
        op.f("uq_category_properties_uuid_1c"),
        "category_properties",
        type_="unique",
    )
    op.drop_column("category_properties", "uuid_1c")
    # ### end Alembic commands ###