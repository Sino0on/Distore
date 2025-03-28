"""change brand's image field type to str

Revision ID: 0e1fc18ab310
Revises: 553306823663
Create Date: 2024-11-24 20:38:48.383816

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0e1fc18ab310"
down_revision: Union[str, None] = "553306823663"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "brands", sa.Column("image_url", sa.String(), nullable=False)
    )
    op.drop_column("brands", "image")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "brands",
        sa.Column("image", sa.VARCHAR(), autoincrement=False, nullable=True),
    )
    op.drop_column("brands", "image_url")
    # ### end Alembic commands ###
