from decimal import Decimal

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app import controllers
from app.main import app
from app.models.tax_brackets import TaxBrackets
from app.settings import Settings


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


class TestTaxCalculator:
    @pytest.mark.parametrize(
        "body",
        [
            ("something"),
            ({}),
            ({"tax_year": "random", "yearly_salary": 50000}),
            ({"tax_year": 2022, "yearly_salary": "random"}),
        ],
    )
    def test_validation_errors(self, client: TestClient, body):
        response = client.post("/", json=body)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.parametrize(
        "fixture_name,expected_detail,expected_status_code",
        [
            (
                "fetch_tax_brackets_invalid_tax_brackets",
                controllers.TAX_YEAR_CANNOT_LOAD,
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            ),
            (
                "fetch_tax_brackets_not_found",
                controllers.TAX_YEAR_NOT_SUPPORTED,
                status.HTTP_404_NOT_FOUND,
            ),
            (
                "fetch_tax_brackets_server_error",
                controllers.TAX_YEAR_CANNOT_FETCH,
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            ),
            (
                "fetch_tax_brackets_timeout",
                controllers.TAX_YEAR_CANNOT_FETCH,
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            ),
            (
                "fetch_tax_brackets_retry_invalid_tax_brackets",
                controllers.TAX_YEAR_CANNOT_LOAD,
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            ),
        ],
    )
    def test_fetch_tax_brackets_errors(
        self,
        request,
        client: TestClient,
        settings: Settings,
        fixture_name: str,
        expected_detail: str,
        expected_status_code: int,
    ):
        request.getfixturevalue(fixture_name)

        tax_year = 2019

        response = client.post(
            "/",
            json={"tax_year": tax_year, "yearly_salary": 50000},
        )

        detail = response.json()["detail"]

        assert response.status_code == expected_status_code
        assert detail == expected_detail.format(tax_year=tax_year)

    @pytest.mark.parametrize(
        "tax_year,yearly_salary,expected_marginal_taxes",
        [
            (2018, -10000, [0, 0, 0]),
            (2019, 0, [0, 0, 0]),
            (2019, 5000, [750, 0, 0]),
            (2019, "5000.5", ["750.075", 0, 0]),
            (2019, 10000, [1500, 0, 0]),
            (2019, 15000, [1500, 1250, 0]),
            (2019, 20000, [1500, 2500, 0]),
            (2019, "45000.5", [1500, 2500, "8750.175"]),
        ],
    )
    def test_tax_calculator(
        self,
        client: TestClient,
        settings: Settings,
        tax_brackets1: TaxBrackets,
        fetch_tax_brackets1,
        tax_year,
        yearly_salary,
        expected_marginal_taxes,
    ):
        response = client.post(
            "/",
            json={"tax_year": tax_year, "yearly_salary": yearly_salary},
        )

        yearly_salary = Decimal(yearly_salary)

        expected_total_tax = sum(map(Decimal, expected_marginal_taxes))
        expected_marginal_taxes = list(map(float, expected_marginal_taxes))

        if yearly_salary <= 0:
            expected_effective_tax_rate = Decimal(0)
        else:
            expected_effective_tax_rate = expected_total_tax / yearly_salary

        expected_tax_brackets = tax_brackets1.model_dump()["tax_brackets"]
        expected_keys = (
            "total_tax",
            "effective_tax_rate",
            "marginal_taxes",
            "tax_brackets",
        )

        json = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert json["marginal_taxes"] == expected_marginal_taxes
        assert json["total_tax"] == float(expected_total_tax)
        assert json["effective_tax_rate"] == float(expected_effective_tax_rate)
        assert json["tax_brackets"] == expected_tax_brackets
        assert tuple(json.keys()) == expected_keys
