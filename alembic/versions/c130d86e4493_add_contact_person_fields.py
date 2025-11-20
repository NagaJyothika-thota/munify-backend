"""add_contact_person_fields

Revision ID: c130d86e4493
Revises: 5220ddddfcc3
Create Date: 2025-11-20 10:33:01.788737

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c130d86e4493'
down_revision: Union[str, Sequence[str], None] = '5220ddddfcc3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
