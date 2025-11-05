"""add_cascade_delete_to_tasks_project_id

Revision ID: c124ddaefa96
Revises: 169874d2c6fb
Create Date: 2025-10-13 20:29:00.555665

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c124ddaefa96'
down_revision: Union[str, Sequence[str], None] = '169874d2c6fb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop the existing foreign key constraint
    op.drop_constraint('tasks_project_id_fkey', 'tasks', type_='foreignkey')

    # Add the new foreign key constraint with CASCADE DELETE
    op.create_foreign_key(
        'tasks_project_id_fkey',
        'tasks', 'projects',
        ['project_id'], ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop the cascade foreign key constraint
    op.drop_constraint('tasks_project_id_fkey', 'tasks', type_='foreignkey')

    # Add back the original foreign key constraint without CASCADE
    op.create_foreign_key(
        'tasks_project_id_fkey',
        'tasks', 'projects',
        ['project_id'], ['id']
    )
