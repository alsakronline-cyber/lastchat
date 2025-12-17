"""add_rich_product_fields

Revision ID: 2e9c2f6d0a7b
Revises: 1e9c2f6d0a7a
Create Date: 2025-12-17 18:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2e9c2f6d0a7b'
down_revision = '1e9c2f6d0a7a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns to products table
    op.add_column('products', sa.Column('technical_drawings', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('products', sa.Column('documents', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('products', sa.Column('custom_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('products', sa.Column('family_group', sa.String(length=255), nullable=True)) 
    # Note: family_group might already exist or not depending on initial schema drift, 
    # but based on 1e9c2f6d0a7a it was NOT there (only manufacturer, category etc). 
    # In my updated models.py I saw it. So I am adding it here.

def downgrade() -> None:
    op.drop_column('products', 'family_group')
    op.drop_column('products', 'custom_data')
    op.drop_column('products', 'documents')
    op.drop_column('products', 'technical_drawings')
