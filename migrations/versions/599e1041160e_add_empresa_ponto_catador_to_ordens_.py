"""add_empresa_ponto_catador_to_ordens_servico

Revision ID: 599e1041160e
Revises: b2c3d4e5f6a7
Create Date: 2025-11-02 08:24:36.093542

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '599e1041160e'
down_revision: Union[str, None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Adiciona colunas de relacionamento à tabela ordens_servico
    op.add_column(
        'ordens_servico',
        sa.Column('empresa_id', sa.Integer(), nullable=True)
    )
    op.add_column(
        'ordens_servico',
        sa.Column('ponto_coleta_id', sa.Integer(), nullable=True)
    )
    op.add_column(
        'ordens_servico',
        sa.Column('catador_id', sa.Integer(), nullable=True)
    )
    
    # Cria foreign keys
    op.create_foreign_key(
        'fk_ordens_servico_empresa_id',
        'ordens_servico',
        'empresas',
        ['empresa_id'],
        ['id']
    )
    op.create_foreign_key(
        'fk_ordens_servico_ponto_coleta_id',
        'ordens_servico',
        'pontos_coleta',
        ['ponto_coleta_id'],
        ['id']
    )
    op.create_foreign_key(
        'fk_ordens_servico_catador_id',
        'ordens_servico',
        'catadores',
        ['catador_id'],
        ['id']
    )


def downgrade() -> None:
    # Remove foreign keys
    op.drop_constraint(
        'fk_ordens_servico_catador_id',
        'ordens_servico',
        type_='foreignkey'
    )
    op.drop_constraint(
        'fk_ordens_servico_ponto_coleta_id',
        'ordens_servico',
        type_='foreignkey'
    )
    op.drop_constraint(
        'fk_ordens_servico_empresa_id',
        'ordens_servico',
        type_='foreignkey'
    )
    
    # Remove colunas
    op.drop_column('ordens_servico', 'catador_id')
    op.drop_column('ordens_servico', 'ponto_coleta_id')
    op.drop_column('ordens_servico', 'empresa_id')
