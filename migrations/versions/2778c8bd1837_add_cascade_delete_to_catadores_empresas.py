"""add_cascade_delete_to_catadores_empresas

Revision ID: 2778c8bd1837
Revises: b0ca20908a9d
Create Date: 2025-11-02 12:11:22.196340

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2778c8bd1837'
down_revision: Union[str, None] = 'b0ca20908a9d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop as constraints antigas
    op.drop_constraint(
        'catadores_empresas_catador_id_fkey',
        'catadores_empresas',
        type_='foreignkey'
    )
    op.drop_constraint(
        'catadores_empresas_empresa_id_fkey',
        'catadores_empresas',
        type_='foreignkey'
    )
    
    # Recria as constraints com CASCADE
    op.create_foreign_key(
        'catadores_empresas_catador_id_fkey',
        'catadores_empresas',
        'catadores',
        ['catador_id'],
        ['id'],
        ondelete='CASCADE'
    )
    op.create_foreign_key(
        'catadores_empresas_empresa_id_fkey',
        'catadores_empresas',
        'empresas',
        ['empresa_id'],
        ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    # Remove as constraints com CASCADE
    op.drop_constraint(
        'catadores_empresas_catador_id_fkey',
        'catadores_empresas',
        type_='foreignkey'
    )
    op.drop_constraint(
        'catadores_empresas_empresa_id_fkey',
        'catadores_empresas',
        type_='foreignkey'
    )
    
    # Recria as constraints sem CASCADE
    op.create_foreign_key(
        'catadores_empresas_catador_id_fkey',
        'catadores_empresas',
        'catadores',
        ['catador_id'],
        ['id']
    )
    op.create_foreign_key(
        'catadores_empresas_empresa_id_fkey',
        'catadores_empresas',
        'empresas',
        ['empresa_id'],
        ['id']
    )
