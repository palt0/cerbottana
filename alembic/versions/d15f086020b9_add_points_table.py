"""Add points table

Revision ID: d15f086020b9
Revises: 7e97091b66b0
Create Date: 2020-09-02 13:17:25.222055

"""
from sqlalchemy import Column, Integer, String, UniqueConstraint

from alembic import op

# revision identifiers, used by Alembic.
revision = "d15f086020b9"
down_revision = "7e97091b66b0"
branch_labels = None
depends_on = None


def upgrade(engine_name):
    globals()["upgrade_%s" % engine_name]()


def downgrade(engine_name):
    globals()["downgrade_%s" % engine_name]()


def upgrade_database():
    op.create_table(
        "points",
        Column("id", Integer, primary_key=True),
        Column("userid", String, nullable=False),
        Column("roomid", String, nullable=False),
        Column("date", String, nullable=False),
        Column("tourpoints", Integer, nullable=False),
        Column("games", Integer, nullable=False),
        Column("first", Integer, nullable=False),
        Column("second", Integer, nullable=False),
        Column("third", Integer, nullable=False),
        UniqueConstraint("userid", "date", sqlite_on_conflict="REPLACE"),
    )


def downgrade_database():
    pass


def upgrade_logs():
    pass


def downgrade_logs():
    pass
