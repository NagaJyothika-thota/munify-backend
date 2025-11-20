"""add_contact_person_fields

Revision ID: 5220ddddfcc3
Revises: ef16018892ed
Create Date: 2025-11-20 10:29:56.317205

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5220ddddfcc3'
down_revision: Union[str, Sequence[str], None] = 'ef16018892ed'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
