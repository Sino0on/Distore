"""add enum to order status field

Revision ID: c97e67c8e919
Revises: c14e859600fb
Create Date: 2024-08-13 04:25:48.598500

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c97e67c8e919"
down_revision: Union[str, None] = "c14e859600fb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute("CREATE TYPE orderstatus AS ENUM ('created', 'in_progress', 'completed', 'canceled', 'paid');")

    op.execute("ALTER TABLE orders ALTER COLUMN status TYPE orderstatus USING status::orderstatus")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute("ALTER TABLE orders ALTER COLUMN status TYPE varchar")

    op.execute("DROP TYPE orderstatus;")
    # ### end Alembic commands ###
