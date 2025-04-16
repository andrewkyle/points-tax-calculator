import httpx
from fastapi import HTTPException, status
from pydantic import ValidationError

from app.models.tax_brackets import TaxBrackets
from app.settings import Settings, settings

TAX_YEAR_CANNOT_LOAD = "Tax year {tax_year} cannot be loaded."
TAX_YEAR_CANNOT_FETCH = "Tax year {tax_year} cannot be fetched."
TAX_YEAR_NOT_SUPPORTED = "Tax year {tax_year} not supported."


def _get_settings() -> Settings:
    return settings


def _fetch_tax_brackets(url: str, timeout: int) -> httpx.Response:
    return httpx.get(url, timeout=timeout)


def fetch_tax_brackets(tax_year: int) -> TaxBrackets:
    """Fetch tax brackets for a given tax year.

    Throws `HTTPException` if the tax brackets not found or cannot be loaded.

    :param tax_year: Tax year.
    :type tax_year: int
    :return: Tax brackets.
    :rtype: TaxBrackets
    """

    s = _get_settings()
    url = s.tax_year_url.format(tax_year=tax_year)

    for retry_count in range(s.tax_year_retry + 1):
        try:
            response = _fetch_tax_brackets(url, s.tax_year_timeout)
        except httpx.TimeoutException:
            continue  # Retry if timed out.

        match response.status_code:
            case httpx.codes.OK:
                try:
                    return TaxBrackets.model_validate_json(response.text)
                except ValidationError:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=TAX_YEAR_CANNOT_LOAD.format(tax_year=tax_year),
                    )
            case httpx.codes.NOT_FOUND:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=TAX_YEAR_NOT_SUPPORTED.format(tax_year=tax_year),
                )

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=TAX_YEAR_CANNOT_FETCH.format(tax_year=tax_year),
    )
