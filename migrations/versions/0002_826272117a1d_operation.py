"""Operation

Revision ID: 826272117a1d
Revises: 5c98b21f6ec2
Create Date: 2023-05-03 20:41:23.150734

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '826272117a1d'
down_revision = '5c98b21f6ec2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('operation',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('quantity', sa.String(), nullable=True),
                    sa.Column('figi', sa.String(), nullable=True),
                    sa.Column('instrument_type', sa.String(), nullable=True),
                    sa.Column('date', sa.TIMESTAMP(), nullable=True),
                    sa.Column('type', sa.String(), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('operation')
    # ### end Alembic commands ###