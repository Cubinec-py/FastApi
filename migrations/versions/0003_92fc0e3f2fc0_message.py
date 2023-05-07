"""Message

Revision ID: 92fc0e3f2fc0
Revises: 826272117a1d
Create Date: 2023-05-07 19:05:11.979794

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '92fc0e3f2fc0'
down_revision = '826272117a1d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('message',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('message', sa.String(), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('message')
    # ### end Alembic commands ###