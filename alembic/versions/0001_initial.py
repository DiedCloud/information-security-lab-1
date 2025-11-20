"""initial

Revision ID: 0001_initial
Revises:
Create Date: 2025-11-19 00:00:00.000000

"""

import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # users table
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("login", sa.String(length=150), nullable=False, unique=True),
        sa.Column("password", sa.String(length=255), nullable=False),
    )

    # publications table
    op.create_table(
        "publications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("author_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    )

    op.create_index("ix_publications_created_at", "publications", ["created_at"])
    op.create_index("ix_publications_author_id", "publications", ["author_id"])

    # create trigger function
    op.execute("""
    CREATE FUNCTION update_updated_at_column() RETURNS trigger AS $$
    BEGIN
        NEW.updated_at = now();
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """)

    # create trigger on publications
    op.execute("""
    CREATE TRIGGER trg_update_publications_updated_at
    BEFORE UPDATE ON publications
    FOR EACH ROW
    EXECUTE PROCEDURE update_updated_at_column();
    """)


def downgrade() -> None:
    op.drop_index("ix_publications_author_id", table_name="publications")
    op.drop_index("ix_publications_created_at", table_name="publications")
    op.drop_table("publications")
    op.drop_table("users")

    op.execute("DROP TRIGGER IF EXISTS trg_update_publications_updated_at ON publications;")
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column();")
