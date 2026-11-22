
"""add lead AI analysis details

Revision ID: e03ca34f79ea
Revises: 362ff80fad3a
Create Date: 2026-11-16 17:55:06.610753
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e03ca34f79ea'
down_revision: Union[str, Sequence[str], None] = '362ff80fad3a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'leads',
        sa.Column('score_breakdown', sa.JSON(), nullable=True)
    )
    op.add_column(
        'leads',
        sa.Column('enrichment_evidence', sa.JSON(), nullable=True)
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('leads', 'enrichment_evidence')
    op.drop_column('leads', 'score_breakdown')
