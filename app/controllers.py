import httpx
from fastapi import HTTPException, status
from pydantic import ValidationError

from app.models.tax_brackets import TaxBrackets
from app.settings import Settings, settings


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

    for _ in range(s.tax_year_retry):
        response = _fetch_tax_brackets(
            s.tax_year_url.format(tax_year=tax_year),
            s.tax_year_timeout,
        )

        match response.status_code:
            case httpx.codes.OK:
                try:
                    return TaxBrackets.model_validate_json(response.text)
                except ValidationError:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Tax year {tax_year} cannot be loaded.",
                    )
            case httpx.codes.NOT_FOUND:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Tax year {tax_year} not supported.",
                )

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Tax year {tax_year} cannot be fetched.",
    )
