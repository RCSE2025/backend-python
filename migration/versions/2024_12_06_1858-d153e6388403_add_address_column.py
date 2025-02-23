"""add address column

Revision ID: d153e6388403
Revises: 84d77f110e99
Create Date: 2024-12-06 18:58:39.059898

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d153e6388403"
down_revision: Union[str, None] = "84d77f110e99"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "regional_agents", sa.Column("address", sa.String(length=200), nullable=False)
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("regional_agents", "address")
    # ### end Alembic commands ###
