"""Expanding the database

Revision ID: 7ed344e7884d
Revises: db7f3a4caf02
Create Date: 2025-03-03 08:50:19.193482

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7ed344e7884d'
down_revision = 'db7f3a4caf02'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('receipt_scans',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('image_url', sa.String(length=255), nullable=True),
    sa.Column('ocr_text', sa.Text(), nullable=True),
    sa.Column('confidence_score', sa.Float(), nullable=True),
    sa.Column('merchant_name', sa.String(length=255), nullable=True),
    sa.Column('purchase_date', sa.DateTime(), nullable=True),
    sa.Column('items_detected', sa.JSON(), nullable=True),
    sa.Column('total_amount', sa.Numeric(), nullable=True),
    sa.Column('status', sa.String(length=50), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('processed_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('receipt_scans')
    # ### end Alembic commands ###
