import asyncio

from file2formai.core.config import get_settings
from file2formai.core.database import Database
from file2formai.development.seed import (
    DEVELOPMENT_ADMIN_USER_ID,
    HARBORLINE_ORGANIZATION_ID,
    NORTHSTAR_ORGANIZATION_ID,
    seed_development_data,
)


async def run() -> None:
    settings = get_settings()
    if settings.environment != "development":
        raise RuntimeError("development seed is disabled outside the development environment")

    database = Database(settings)
    try:
        async with database.session() as session:
            await seed_development_data(session)
    finally:
        await database.dispose()

    print("Development data is ready.")
    print(f"Development user: {DEVELOPMENT_ADMIN_USER_ID}")
    print(f"Northstar organization: {NORTHSTAR_ORGANIZATION_ID}")
    print(f"Harborline organization: {HARBORLINE_ORGANIZATION_ID}")


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
