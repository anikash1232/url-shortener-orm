"""Shared configuration, hooks, and fixtures for the test suite.

The `conftest.py` file is a special pytest file that allows for the sharing of fixtures
across multiple files, as well as the implementation of pytest hooks to customize the test
execution lifecycle (e.g., adding command-line options or modifying how tests are collected).
"""

from collections.abc import Iterator

import pytest
from sqlmodel import Session, SQLModel, create_engine

TEST_POSTGRES_URL = "postgresql://postgres:password@db:5432/links_db_test"


@pytest.fixture
def db_session() -> Iterator[Session]:
    """Provide a clean database session against links_db_test for each test."""
    test_engine = create_engine(TEST_POSTGRES_URL)
    SQLModel.metadata.drop_all(test_engine)
    SQLModel.metadata.create_all(test_engine)
    with Session(test_engine) as session:
        yield session
    SQLModel.metadata.drop_all(test_engine)
    test_engine.dispose()


def pytest_addoption(parser: pytest.Parser) -> None:
    """Registers custom command-line options with pytest.

    This hook is called during the configuration phase of the pytest lifecycle. It allows
    adding new flags that can then be checked during test collection or execution.

    Args:
        parser (pytest.Parser): The parser object used to add command-line options.
    """
    parser.addoption(
        "--integration",
        action="store_true",
        default=False,
        help="Run integration tests",
    )


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    """Modifies the collection of test items before they are executed.

    This hook is called after pytest has collected all test files and items, but before
    any tests are run. It is used here to filter out tests marked as 'integration' unless
    the `--integration` flag was provided at the command line.

    Args:
        config (pytest.Config): The pytest configuration object.
        items (list[pytest.Item]): The list of collected test items to be modified.
    """
    if config.getoption("--integration"):
        return
    skip_integration = pytest.mark.skip(reason="use --integration to run")
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip_integration)
