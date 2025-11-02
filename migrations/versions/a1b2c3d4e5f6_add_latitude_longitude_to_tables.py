"""add_latitude_longitude_to_tables

Revision ID: a1b2c3d4e5f6
Revises: dfdae5b48dea
Create Date: 2025-11-02 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'dfdae5b48dea'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Adiciona campos latitude e longitude nas tabelas:
    - solicitacoes_coleta
    - empresas
    - pontos_coleta
    """
    # Adiciona latitude e longitude em solicitacoes_coleta
    op.add_column(
        'solicitacoes_coleta',
        sa.Column('latitude', sa.Float(), nullable=True)
    )
    op.add_column(
        'solicitacoes_coleta',
        sa.Column('longitude', sa.Float(), nullable=True)
    )

    # Adiciona latitude e longitude em empresas
    op.add_column(
        'empresas',
        sa.Column('latitude', sa.Float(), nullable=True)
    )
    op.add_column(
        'empresas',
        sa.Column('longitude', sa.Float(), nullable=True)
    )

    # Adiciona latitude e longitude em pontos_coleta
    op.add_column(
        'pontos_coleta',
        sa.Column('latitude', sa.Float(), nullable=True)
    )
    op.add_column(
        'pontos_coleta',
        sa.Column('longitude', sa.Float(), nullable=True)
    )


def downgrade() -> None:
    """
    Remove os campos latitude e longitude adicionados.
    """
    # Remove de pontos_coleta
    op.drop_column('pontos_coleta', 'longitude')
    op.drop_column('pontos_coleta', 'latitude')

    # Remove de empresas
    op.drop_column('empresas', 'longitude')
    op.drop_column('empresas', 'latitude')

    # Remove de solicitacoes_coleta
    op.drop_column('solicitacoes_coleta', 'longitude')
    op.drop_column('solicitacoes_coleta', 'latitude')

