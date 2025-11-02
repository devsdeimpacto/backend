"""add_endereco_to_empresas

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2025-11-02 12:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Adiciona campo endereco na tabela empresas.
    """
    op.add_column(
        'empresas',
        sa.Column('endereco', sa.String(length=500), nullable=True)
    )
    
    # Após adicionar, podemos definir como NOT NULL após preencher
    # os dados existentes (se houver). Por enquanto, deixa nullable.


def downgrade() -> None:
    """
    Remove o campo endereco da tabela empresas.
    """
    op.drop_column('empresas', 'endereco')

