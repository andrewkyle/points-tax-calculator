from unittest.mock import call

import pytest
from fastapi import HTTPException, status

from app import controllers
from app.conftest import TAX_YEAR_RETRY
from app.models.tax_brackets import TaxBrackets
from app.settings import Settings


class TestFetchTaxBrackets:
    @pytest.mark.parametrize(
        (
            "fixture_name,"
            "expected_detail,"
            "expected_status_code,"
            "expected_retry_count"
        ),
        [
            (
                "fetch_tax_brackets_invalid_tax_brackets",
                controllers.TAX_YEAR_CANNOT_LOAD,
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                0,
            ),
            (
                "fetch_tax_brackets_not_found",
                controllers.TAX_YEAR_NOT_SUPPORTED,
                status.HTTP_404_NOT_FOUND,
                0,
            ),
            (
                "fetch_tax_brackets_server_error",
                controllers.TAX_YEAR_CANNOT_FETCH,
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                TAX_YEAR_RETRY,
            ),
            (
                "fetch_tax_brackets_timeout",
                controllers.TAX_YEAR_CANNOT_FETCH,
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                TAX_YEAR_RETRY,
            ),
            (
                "fetch_tax_brackets_retry_invalid_tax_brackets",
                controllers.TAX_YEAR_CANNOT_LOAD,
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                TAX_YEAR_RETRY - 1,
            ),
        ],
    )
    def test_fetch_tax_brackets_errors(
        self,
        request,
        settings: Settings,
        fixture_name: str,
        expected_detail: str,
        expected_status_code: int,
        expected_retry_count: int,
    ):
        _fetch_tax_brackets = request.getfixturevalue(fixture_name)

        tax_year = 2022
        url = settings.tax_year_url.format(tax_year=tax_year)
        timeout = settings.tax_year_timeout
        expected_calls = [call(url, timeout)] * (expected_retry_count + 1)

        with pytest.raises(HTTPException) as exc:
            controllers.fetch_tax_brackets(tax_year)

        assert exc.value.detail == expected_detail.format(tax_year=tax_year)
        assert exc.value.status_code == expected_status_code
        assert _fetch_tax_brackets.mock_calls == expected_calls

    def test_fetch_tax_brackets(
        self,
        fetch_tax_brackets1,
        settings: Settings,
        tax_brackets1: TaxBrackets,
    ):
        tax_year = 2022
        url = settings.tax_year_url.format(tax_year=tax_year)
        timeout = settings.tax_year_timeout

        tax_brackets = controllers.fetch_tax_brackets(tax_year)

        assert tax_brackets == tax_brackets1
        assert fetch_tax_brackets1.mock_calls == [call(url, timeout)]
