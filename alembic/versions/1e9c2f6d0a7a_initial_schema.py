"""initial_schema

Revision ID: 1e9c2f6d0a7a
Revises: 
Create Date: 2025-12-13 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '1e9c2f6d0a7a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Products Table
    op.create_table('products',
        sa.Column('sku_id', sa.String(length=100), primary_key=True),
        sa.Column('product_name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True), # Added missing column
        sa.Column('manufacturer', sa.String(length=100), nullable=True),
        sa.Column('specifications', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('relationships', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('embedding_text', sa.Text(), nullable=True),
        sa.Column('datasheet_url', sa.String(length=500), nullable=True),
        sa.Column('images', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('pricing', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('language', sa.String(length=10), nullable=True),
        sa.Column('source', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_products_manufacturer', 'products', ['manufacturer'])
    op.create_index('ix_products_name', 'products', ['product_name'])

    # 2. CRM Contacts Table
    op.create_table('contacts',
        sa.Column('contact_id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(length=150), nullable=False),
        sa.Column('email', sa.String(length=150), nullable=False),
        sa.Column('company', sa.String(length=150), nullable=True),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('industry', sa.String(length=100), nullable=True),
        sa.Column('country', sa.String(length=100), nullable=True),
        sa.Column('preferences', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_contacts_email', 'contacts', ['email'], unique=True)

    # 3. Quotations Table
    op.create_table('quotations',
        sa.Column('quotation_id', sa.String(length=50), primary_key=True),
        sa.Column('contact_id', sa.Integer(), sa.ForeignKey('contacts.contact_id'), nullable=False),
        sa.Column('sku_list', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('quantities', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('delivery_country', sa.String(length=100), nullable=True),
        sa.Column('status', sa.String(length=20), server_default='DRAFT', nullable=False),
        sa.Column('total_price_estimate', sa.Float(), nullable=True),
        sa.Column('expiry_date', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    )

    # 4. Interaction Logs
    op.create_table('interaction_logs',
        sa.Column('log_id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.String(length=100), nullable=True),
        sa.Column('session_id', sa.String(length=100), nullable=True),
        sa.Column('query', sa.Text(), nullable=True),
        sa.Column('recommended_sku', sa.String(length=100), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('response_time_ms', sa.Integer(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('interaction_logs')
    op.drop_table('quotations')
    op.drop_table('contacts')
    op.drop_index('ix_products_name', table_name='products')
    op.drop_index('ix_products_manufacturer', table_name='products')
    op.drop_table('products')
