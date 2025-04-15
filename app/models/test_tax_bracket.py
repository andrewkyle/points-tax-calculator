from decimal import Decimal

import pytest

from app.models.tax_bracket import TaxBracket


class TestTaxBracket:
    @pytest.mark.parametrize(
        "bracket_dict,amount,expected_tax",
        [
            ({"min": 0, "max": 10000, "rate": 0.15}, -1000, 0),
            ({"min": 0, "max": 10000, "rate": 0.15}, 0, 0),
            ({"min": 0, "max": 10000, "rate": 0.15}, 5000, 750),
            ({"min": 0, "max": 10000, "rate": 0.15}, "6000.5", "900.075"),
            ({"min": 0, "max": 10000, "rate": 0.15}, 15000, 1500),
            ({"min": 10000, "max": 20000, "rate": 0.25}, -1000, 0),
            ({"min": 10000, "max": 20000, "rate": 0.25}, 0, 0),
            ({"min": 10000, "max": 20000, "rate": 0.25}, 9000, 0),
            ({"min": 10000, "max": 20000, "rate": 0.25}, 10000, 0),
            ({"min": 10000, "max": 20000, "rate": 0.25}, 15000, 1250),
            (
                {"min": 10000, "max": 20000, "rate": 0.25},
                "16000.5",
                "1500.125",
            ),
            ({"min": 10000, "max": 20000, "rate": 0.25}, 25000, 2500),
            ({"min": 20000, "rate": 0.35}, -1000, 0),
            ({"min": 20000, "rate": 0.35}, 0, 0),
            ({"min": 20000, "rate": 0.35}, 15000, 0),
            ({"min": 20000, "rate": 0.35}, 20000, 0),
            ({"min": 20000, "rate": 0.35}, "31000.5", "3850.175"),
            ({"min": 20000, "rate": 0.35}, 50000, 10500),
        ],
    )
    def test_marginal_tax(self, bracket_dict, amount, expected_tax):
        bracket = TaxBracket(**bracket_dict)
        amount = Decimal(amount)
        expected_tax = Decimal(expected_tax)

        assert bracket.marginal_tax(amount) == expected_tax
