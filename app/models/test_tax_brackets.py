from decimal import Decimal

import pytest

from app.models.tax_bracket import TaxBracket
from app.models.tax_brackets import TaxBrackets


@pytest.fixture
def tax_brackets():
    return TaxBrackets(
        tax_brackets=[
            TaxBracket(min=0, max=10000, rate=0.15),
            TaxBracket(min=10000, max=20000, rate=0.25),
            TaxBracket(min=20000, rate=0.35),
        ],
    )


class TestTaxBrackets:
    @pytest.mark.parametrize(
        "amount,expected_marginal_taxes",
        [
            (-10000, [0, 0, 0]),
            (0, [0, 0, 0]),
            (5000, [750, 0, 0]),
            ("15000.5", [1500, "1250.125", 0]),
            ("25000.5", [1500, 2500, "1750.175"]),
            (25000, [1500, 2500, 1750]),
        ],
    )
    def test_compute_tax(
        self,
        tax_brackets: TaxBrackets,
        amount,
        expected_marginal_taxes,
    ):
        amount = Decimal(amount)
        expected_marginal_taxes = list(map(Decimal, expected_marginal_taxes))

        expected_total_tax = sum(expected_marginal_taxes)

        if amount <= 0:
            expected_effective_tax_rate = Decimal(0)
        else:
            expected_effective_tax_rate = expected_total_tax / amount

        assert tax_brackets.compute_tax(amount) == (
            expected_total_tax,
            expected_effective_tax_rate,
            expected_marginal_taxes,
        )
