from decimal import Decimal

from pydantic import BaseModel

from app.models.tax_bracket import TaxBracket


class TaxBrackets(BaseModel):
    """A class used to represent a list of tax brackets."""

    tax_brackets: list[TaxBracket]

    def compute_tax(
        self,
        amount: Decimal,
    ) -> tuple[Decimal, Decimal, list[Decimal]]:
        """Compute tax given an amount.

        :param amount: Amount to compute tax against.
        :type amount: Decimal
        :return: Total tax, effective tax rates and marginal taxes.
        :rtype: tuple[Decimal, Decimal, list[Decimal]]
        """

        marginal_taxes = [
            bracket.marginal_tax(amount) for bracket in self.tax_brackets
        ]

        total_tax = sum(marginal_taxes)

        effective_tax_rate = Decimal(0) if amount <= 0 else total_tax / amount

        return total_tax, effective_tax_rate, marginal_taxes
