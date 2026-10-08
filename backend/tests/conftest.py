import os

os.environ.setdefault(
    "F2F_DATABASE_URL",
    "postgresql+asyncpg://unit_test:unit_test@127.0.0.1:1/unit_test",
)
os.environ.setdefault("F2F_ENVIRONMENT", "test")
