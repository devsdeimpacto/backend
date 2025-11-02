"""add_cascade_delete_to_ordem_servico

Revision ID: b0ca20908a9d
Revises: c3d4e5f6a7b8
Create Date: 2025-11-02 10:02:46.300682

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b0ca20908a9d'
down_revision: Union[str, None] = 'c3d4e5f6a7b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop a constraint antiga
    op.drop_constraint(
        'ordens_servico_solicitacao_id_fkey',
        'ordens_servico',
        type_='foreignkey'
    )
    
    # Recria a constraint com CASCADE
    op.create_foreign_key(
        'ordens_servico_solicitacao_id_fkey',
        'ordens_servico',
        'solicitacoes_coleta',
        ['solicitacao_id'],
        ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    # Remove a constraint com CASCADE
    op.drop_constraint(
        'ordens_servico_solicitacao_id_fkey',
        'ordens_servico',
        type_='foreignkey'
    )
    
    # Recria a constraint sem CASCADE
    op.create_foreign_key(
        'ordens_servico_solicitacao_id_fkey',
        'ordens_servico',
        'solicitacoes_coleta',
        ['solicitacao_id'],
        ['id']
    )
