"""nullable=false category uuid_1c field

Revision ID: 0d259e0c14a8
Revises: 51ecb79819c6
Create Date: 2024-09-18 19:30:53.289158

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0d259e0c14a8"
down_revision: Union[str, None] = "51ecb79819c6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "categories", "uuid_1c", existing_type=sa.VARCHAR(), nullable=False
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "categories", "uuid_1c", existing_type=sa.VARCHAR(), nullable=True
    )
    # ### end Alembic commands ###