"""Added last_login_at and rename date to created_at

Revision ID: b51bbc807211
Revises: 438de6673b57
Create Date: 2024-10-27 19:26:57.980078

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql import func

from migrations.utils import column_exists

# revision identifiers, used by Alembic.
revision = 'b51bbc807211'
down_revision = '438de6673b57'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('task', schema=None) as batch_op:
        if not column_exists('task', 'created_at'):
            batch_op.add_column(sa.Column('created_at', sa.DateTime(), nullable=False, server_default=func.now()))
        if column_exists('task', 'date'):
            batch_op.drop_column('date')

    with op.batch_alter_table('user', schema=None) as batch_op:
        # Шаг 1: Временно устанавливаем значение по умолчанию "user" для новых записей
        if not column_exists('user', 'role'):
            batch_op.add_column(
                sa.Column('role', sa.Enum('admin', 'user', 'support', 'moderator', 'analyst', name='user_roles'),
                          nullable=False, server_default='user'))
        if not column_exists('user', 'last_login_at'):
            batch_op.add_column(sa.Column('last_login_at', sa.DateTime(), nullable=False, server_default=func.now()))
        if not column_exists('user', 'created_at'):
            batch_op.add_column(sa.Column('created_at', sa.DateTime(), nullable=False, server_default=func.now()))

        if column_exists('user', 'date'):
            batch_op.drop_column('date')
        if column_exists('user', 'admin'):
            batch_op.drop_column('admin')

    # Шаг 3: Удаляем временное значение по умолчанию
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('role', server_default=None)


def downgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('admin', sa.BOOLEAN(), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('date', sa.DateTime(), autoincrement=False, nullable=False))
        batch_op.drop_column('created_at')
        batch_op.drop_column('last_login_at')
        batch_op.drop_column('role')

    with op.batch_alter_table('task', schema=None) as batch_op:
        batch_op.add_column(sa.Column('date', sa.DateTime(), autoincrement=False, nullable=False))
        batch_op.drop_column('created_at')

    # Удаляем Enum тип user_roles
    op.execute("DROP TYPE user_roles")
