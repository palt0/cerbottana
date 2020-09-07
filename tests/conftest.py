import pytest
from _pytest.config.argparsing import Parser
from _pytest.fixtures import FixtureRequest


def pytest_addoption(parser: Parser) -> None:
    parser.addoption(
        "--golden",
        dest="golden",
        action="store_true",
        help="generate golden files",
    )


@pytest.fixture(scope="session")
def generate_golden(request: FixtureRequest) -> bool:
    return bool(request.config.option.golden)
