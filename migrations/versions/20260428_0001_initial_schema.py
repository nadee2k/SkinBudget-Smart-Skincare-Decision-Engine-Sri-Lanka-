"""Initial schema

Revision ID: 20260428_0001
Revises:
Create Date: 2026-04-28 00:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260428_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("user_id", sa.String(length=50), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("name", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
    )

    op.create_table(
        "skin_type",
        sa.Column("skin_type_id", sa.String(length=50), primary_key=True),
        sa.Column("name", sa.String(length=50), nullable=False),
    )

    op.create_table(
        "skin_concern",
        sa.Column("concern_id", sa.String(length=50), primary_key=True),
        sa.Column("concern_name", sa.String(length=100), nullable=False),
    )

    op.create_table(
        "brand",
        sa.Column("brand_id", sa.String(length=50), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("country", sa.String(length=100), nullable=True),
    )

    op.create_table(
        "routine_category",
        sa.Column("category_id", sa.String(length=50), primary_key=True),
        sa.Column("category_name", sa.String(length=100), nullable=False),
        sa.Column("step_order", sa.Integer(), nullable=False),
    )

    op.create_table(
        "ingredient",
        sa.Column("ingredient_id", sa.String(length=50), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("inci_name", sa.String(length=150), nullable=True),
    )

    op.create_table(
        "user_skin_profile",
        sa.Column("profile_id", sa.String(length=50), primary_key=True),
        sa.Column("user_id", sa.String(length=50), sa.ForeignKey("users.user_id"), nullable=True),
        sa.Column("skin_type_id", sa.String(length=50), sa.ForeignKey("skin_type.skin_type_id"), nullable=True),
        sa.Column("confidence_score", sa.Float(), nullable=True),
        sa.Column("recorded_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "user_concern",
        sa.Column("user_id", sa.String(length=50), sa.ForeignKey("users.user_id"), primary_key=True),
        sa.Column("concern_id", sa.String(length=50), sa.ForeignKey("skin_concern.concern_id"), primary_key=True),
    )

    op.create_table(
        "product",
        sa.Column("product_id", sa.String(length=50), primary_key=True),
        sa.Column("brand_id", sa.String(length=50), sa.ForeignKey("brand.brand_id"), nullable=True),
        sa.Column("category_id", sa.String(length=50), sa.ForeignKey("routine_category.category_id"), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("price", sa.Float(), nullable=False),
    )

    op.create_table(
        "product_metadata",
        sa.Column("product_id", sa.String(length=50), sa.ForeignKey("product.product_id"), primary_key=True),
        sa.Column("rating", sa.Float(), nullable=True),
        sa.Column("review_count", sa.Integer(), nullable=True),
        sa.Column("popularity_score", sa.Float(), nullable=True),
    )

    op.create_table(
        "product_ingredient",
        sa.Column("product_id", sa.String(length=50), sa.ForeignKey("product.product_id"), primary_key=True),
        sa.Column("ingredient_id", sa.String(length=50), sa.ForeignKey("ingredient.ingredient_id"), primary_key=True),
        sa.Column("role", sa.String(length=50), nullable=True),
        sa.Column("concentration", sa.Float(), nullable=True),
    )

    op.create_table(
        "ingredient_skin_type",
        sa.Column("ingredient_id", sa.String(length=50), sa.ForeignKey("ingredient.ingredient_id"), primary_key=True),
        sa.Column("skin_type_id", sa.String(length=50), sa.ForeignKey("skin_type.skin_type_id"), primary_key=True),
        sa.Column("effect_type", sa.String(length=50), nullable=True),
    )

    op.create_table(
        "ingredient_concern",
        sa.Column("ingredient_id", sa.String(length=50), sa.ForeignKey("ingredient.ingredient_id"), primary_key=True),
        sa.Column("concern_id", sa.String(length=50), sa.ForeignKey("skin_concern.concern_id"), primary_key=True),
        sa.Column("effect_type", sa.String(length=50), nullable=True),
        sa.Column("impact_score", sa.Float(), nullable=True),
    )

    op.create_table(
        "ingredient_conflict",
        sa.Column("ingredient_id_1", sa.String(length=50), sa.ForeignKey("ingredient.ingredient_id"), primary_key=True),
        sa.Column("ingredient_id_2", sa.String(length=50), sa.ForeignKey("ingredient.ingredient_id"), primary_key=True),
        sa.Column("conflict_level", sa.String(length=20), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("ingredient_conflict")
    op.drop_table("ingredient_concern")
    op.drop_table("ingredient_skin_type")
    op.drop_table("product_ingredient")
    op.drop_table("product_metadata")
    op.drop_table("product")
    op.drop_table("user_concern")
    op.drop_table("user_skin_profile")
    op.drop_table("ingredient")
    op.drop_table("routine_category")
    op.drop_table("brand")
    op.drop_table("skin_concern")
    op.drop_table("skin_type")
    op.drop_table("users")

