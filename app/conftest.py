import pytest
from fastapi import status
from httpx import Response, TimeoutException

from app import controllers
from app.models.tax_bracket import TaxBracket
from app.models.tax_brackets import TaxBrackets
from app.settings import Settings

TAX_YEAR_RETRY = 5


@pytest.fixture
def settings(mocker) -> Settings:
    s = Settings(
        tax_year_url="http://localhost:8080/{tax_year}",
        tax_year_retry=TAX_YEAR_RETRY,
        tax_year_timeout=15,
    )

    mocker.patch.object(controllers, "_get_settings", return_value=s)

    return s


@pytest.fixture
def fetch_tax_brackets_invalid_tax_brackets(mocker):
    def _fetch(url: str, timeout: int) -> Response:
        return Response(status.HTTP_200_OK, json={})

    return mocker.patch.object(
        controllers,
        "_fetch_tax_brackets",
        side_effect=_fetch,
    )


@pytest.fixture
def fetch_tax_brackets_not_found(mocker):
    def _fetch(url: str, timeout: int) -> Response:
        return Response(status.HTTP_404_NOT_FOUND)

    return mocker.patch.object(
        controllers,
        "_fetch_tax_brackets",
        side_effect=_fetch,
    )


@pytest.fixture
def fetch_tax_brackets_server_error(mocker):
    def _fetch(url: str, timeout: int) -> Response:
        return Response(status.HTTP_500_INTERNAL_SERVER_ERROR)

    return mocker.patch.object(
        controllers,
        "_fetch_tax_brackets",
        side_effect=_fetch,
    )


@pytest.fixture
def fetch_tax_brackets_timeout(mocker):
    def _fetch(url: str, timeout: int) -> Response:
        raise TimeoutException("")

    return mocker.patch.object(
        controllers,
        "_fetch_tax_brackets",
        side_effect=_fetch,
    )


@pytest.fixture
def fetch_tax_brackets_retry_invalid_tax_brackets(mocker):
    retry_count = -1

    def _fetch(url: str, timeout: int) -> Response:
        nonlocal retry_count
        retry_count += 1

        if retry_count == (TAX_YEAR_RETRY - 1):
            return Response(status.HTTP_200_OK, json={})
        else:
            return Response(status.HTTP_500_INTERNAL_SERVER_ERROR)

    return mocker.patch.object(
        controllers,
        "_fetch_tax_brackets",
        side_effect=_fetch,
    )


@pytest.fixture
def fetch_tax_brackets1(mocker):
    def _fetch(url: str, timeout: int) -> Response:
        return Response(
            status.HTTP_200_OK,
            json={
                "tax_brackets": [
                    {"min": 0, "max": 10000, "rate": 0.15},
                    {"min": 10000, "max": 20000, "rate": 0.25},
                    {"min": 20000, "rate": 0.35},
                ],
            },
        )

    return mocker.patch.object(
        controllers,
        "_fetch_tax_brackets",
        side_effect=_fetch,
    )


@pytest.fixture
def tax_brackets1() -> TaxBrackets:
    return TaxBrackets(
        tax_brackets=[
            TaxBracket(min=0, max=10000, rate=0.15),
            TaxBracket(min=10000, max=20000, rate=0.25),
            TaxBracket(min=20000, rate=0.35),
        ],
    )
