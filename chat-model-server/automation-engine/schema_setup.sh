#!/bin/bash
set -e

echo "Updating alembic/env.py..."

cat << 'EOF' > alembic/env.py
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

from myapp.mymodel import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
EOF


echo "Updating initial schema migration..."

cat << 'EOF' > alembic/versions/1e9c2f6d0a7a_initial_schema.py
"""initial schema

Revision ID: 1e9c2f6d0a7a
Revises:
Create Date: 2024-05-22 10:00:00.000000
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '1e9c2f6d0a7a'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'products',
        sa.Column('sku_id', sa.String(), nullable=False),
        sa.Column('product_name', sa.String(), nullable=False),
        sa.Column('manufacturer', sa.String(), nullable=True),
        sa.Column('specifications', postgresql.JSONB(), nullable=True),
        sa.Column('relationships', postgresql.JSONB(), nullable=True),
        sa.Column('embedding_text', sa.Text(), nullable=True),
        sa.Column('datasheet_url', sa.String(), nullable=True),
        sa.Column('images', postgresql.JSONB(), nullable=True),
        sa.Column('pricing', postgresql.JSONB(), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('language', sa.String(), nullable=True),
        sa.Column('source', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
        sa.PrimaryKeyConstraint('sku_id')
    )

    op.create_index('ix_products_product_name', 'products', ['product_name'])
    op.create_index('ix_products_sku_id', 'products', ['sku_id'])

    op.create_table(
        'contacts',
        sa.Column('contact_id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('company', sa.String()),
        sa.Column('phone', sa.String()),
        sa.Column('industry', sa.String()),
        sa.Column('country', sa.String()),
        sa.Column('preferences', postgresql.JSONB()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'))
    )

    op.create_index('ix_contacts_email', 'contacts', ['email'], unique=True)

    op.create_table(
        'quotations',
        sa.Column('quotation_id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('contact_id', sa.Integer(), sa.ForeignKey('contacts.contact_id')),
        sa.Column('sku_list', postgresql.JSONB()),
        sa.Column('quantities', postgresql.JSONB()),
        sa.Column('delivery_country', sa.String()),
        sa.Column('status', sa.String()),
        sa.Column('total_price_estimate', sa.Float()),
        sa.Column('expiry_date', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'))
    )

    op.create_table(
        'interaction_logs',
        sa.Column('log_id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.String()),
        sa.Column('session_id', sa.String()),
        sa.Column('query', sa.String()),
        sa.Column('recommended_sku', sa.String()),
        sa.Column('confidence_score', sa.Float()),
        sa.Column('response_time_ms', sa.Float()),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'))
    )


def downgrade() -> None:
    op.drop_table('interaction_logs')
    op.drop_table('quotations')
    op.drop_index('ix_contacts_email', table_name='contacts')
    op.drop_table('contacts')
    op.drop_index('ix_products_sku_id', table_name='products')
    op.drop_index('ix_products_product_name', table_name='products')
    op.drop_table('products')
EOF

echo "Schema setup completed."
