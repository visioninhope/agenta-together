"""Added modified_by_id column to apps_db table

Revision ID: 5c29a64204f4
Revises: b80c708c21bb
Create Date: 2024-08-25 17:56:11.732929

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "5c29a64204f4"
down_revision: Union[str, None] = "b80c708c21bb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("app_db", sa.Column("modified_by_id", sa.UUID(), nullable=True))
    op.create_foreign_key(None, "app_db", "users", ["modified_by_id"], ["id"])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "app_db", type_="foreignkey")
    op.drop_constraint(None, "app_db", type_="unique")
    op.drop_column("app_db", "modified_by_id")
    # ### end Alembic commands ###
