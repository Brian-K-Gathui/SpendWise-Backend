"""Expanding the database

Revision ID: db7f3a4caf02
Revises: 77d8d482d7e2
Create Date: 2025-03-03 08:36:26.984202

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'db7f3a4caf02'
down_revision = '77d8d482d7e2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('ai_advisor_profiles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('risk_tolerance', sa.Float(), nullable=False),
    sa.Column('financial_goals', sa.JSON(), nullable=True),
    sa.Column('investment_preferences', sa.JSON(), nullable=True),
    sa.Column('learning_parameters', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('crypto_wallets',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('wallet_address', sa.String(length=255), nullable=True),
    sa.Column('blockchain_type', sa.String(length=50), nullable=True),
    sa.Column('balance_snapshot', sa.JSON(), nullable=True),
    sa.Column('transaction_history', sa.JSON(), nullable=True),
    sa.Column('risk_assessment', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('financial_benchmarks',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('peer_group_params', sa.JSON(), nullable=True),
    sa.Column('comparison_metrics', sa.JSON(), nullable=True),
    sa.Column('insights_generated', sa.JSON(), nullable=True),
    sa.Column('recommendation_score', sa.Float(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('notifications',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('type', sa.String(length=50), nullable=True),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('message', sa.Text(), nullable=False),
    sa.Column('is_read', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('spending_patterns',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('pattern_type', sa.String(length=50), nullable=True),
    sa.Column('pattern_data', sa.JSON(), nullable=True),
    sa.Column('significance_score', sa.Float(), nullable=True),
    sa.Column('recognition_params', sa.JSON(), nullable=True),
    sa.Column('actions_suggested', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('voice_transactions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('audio_url', sa.String(length=255), nullable=True),
    sa.Column('transcription', sa.Text(), nullable=True),
    sa.Column('intent_analysis', sa.JSON(), nullable=True),
    sa.Column('extracted_data', sa.JSON(), nullable=True),
    sa.Column('confidence_score', sa.Float(), nullable=True),
    sa.Column('status', sa.String(length=50), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('processed_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('xr_visualizations',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('visualization_type', sa.String(length=50), nullable=True),
    sa.Column('scene_data', sa.JSON(), nullable=True),
    sa.Column('interaction_metrics', sa.JSON(), nullable=True),
    sa.Column('performance_stats', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('financial_forecasts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('wallet_id', sa.Integer(), nullable=False),
    sa.Column('forecast_type', sa.String(length=50), nullable=True),
    sa.Column('time_range', sa.String(length=50), nullable=True),
    sa.Column('prediction_data', sa.JSON(), nullable=True),
    sa.Column('confidence_interval', sa.JSON(), nullable=True),
    sa.Column('model_version', sa.String(length=50), nullable=True),
    sa.Column('accuracy_metrics', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('valid_until', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['wallet_id'], ['wallets.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('smart_categories',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('parent_category_id', sa.Integer(), nullable=True),
    sa.Column('rules_set', sa.JSON(), nullable=True),
    sa.Column('learning_threshold', sa.Float(), nullable=True),
    sa.Column('confidence_minimum', sa.Float(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['parent_category_id'], ['categories.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('wallet_invitations',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('wallet_id', sa.Integer(), nullable=False),
    sa.Column('invited_by', sa.Integer(), nullable=False),
    sa.Column('invited_email', sa.String(length=120), nullable=False),
    sa.Column('permission_level', sa.String(length=50), nullable=False),
    sa.Column('status', sa.String(length=50), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('expires_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['invited_by'], ['users.id'], ),
    sa.ForeignKeyConstraint(['wallet_id'], ['wallets.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('smart_budgets',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('budget_id', sa.Integer(), nullable=False),
    sa.Column('ai_parameters', sa.JSON(), nullable=True),
    sa.Column('market_conditions', sa.JSON(), nullable=True),
    sa.Column('adjustment_history', sa.JSON(), nullable=True),
    sa.Column('performance_metrics', sa.JSON(), nullable=True),
    sa.Column('suggestion_log', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['budget_id'], ['budgets.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('smart_budgets')
    op.drop_table('wallet_invitations')
    op.drop_table('smart_categories')
    op.drop_table('financial_forecasts')
    op.drop_table('xr_visualizations')
    op.drop_table('voice_transactions')
    op.drop_table('spending_patterns')
    op.drop_table('notifications')
    op.drop_table('financial_benchmarks')
    op.drop_table('crypto_wallets')
    op.drop_table('ai_advisor_profiles')
    # ### end Alembic commands ###
