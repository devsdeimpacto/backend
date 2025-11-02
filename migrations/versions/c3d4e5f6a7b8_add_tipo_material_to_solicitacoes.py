"""add_tipo_material_to_solicitacoes

Revision ID: c3d4e5f6a7b8
Revises: 599e1041160e
Create Date: 2025-11-02 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, None] = '599e1041160e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Adiciona campo tipo_material na tabela solicitacoes_coleta
    """
    # Criar tipo enum no PostgreSQL
    tipo_material_enum = sa.Enum(
        'METAIS',
        'ELETRONICO',
        'PAPEL',
        'PLASTICO',
        'VIDRO',
        'OUTROS',
        name='tipomaterial'
    )
    tipo_material_enum.create(op.get_bind(), checkfirst=True)
    
    # Adiciona coluna tipo_material em solicitacoes_coleta
    op.add_column(
        'solicitacoes_coleta',
        sa.Column(
            'tipo_material',
            tipo_material_enum,
            nullable=False,
            server_default='OUTROS'
        )
    )
    
    # Remove o server_default após adicionar a coluna
    op.alter_column(
        'solicitacoes_coleta',
        'tipo_material',
        server_default=None
    )


def downgrade() -> None:
    """
    Remove o campo tipo_material adicionado.
    """
    # Remove a coluna
    op.drop_column('solicitacoes_coleta', 'tipo_material')
    
    # Remove o tipo enum
    tipo_material_enum = sa.Enum(
        'METAIS',
        'ELETRONICO',
        'PAPEL',
        'PLASTICO',
        'VIDRO',
        'OUTROS',
        name='tipomaterial'
    )
    tipo_material_enum.drop(op.get_bind(), checkfirst=True)

