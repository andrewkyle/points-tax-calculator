from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class TaxBracket(BaseModel):
    """A model used to represent a tax bracket."""

    min: int
    max: Optional[int] = None
    rate: float

    def marginal_tax(self, amount: Decimal) -> Decimal:
        """Compute marginal tax given an amount.

        :param amount: Amount to compute marginal tax against.
        :type amount: Decimal
        :return: Marginal tax.
        :rtype: Decimal
        """

        bracket_min = Decimal(self.min)
        bracket_max = Decimal("Inf" if self.max is None else self.max)
        bracket_rate = Decimal(str(self.rate))

        margin = max(Decimal(0), min(amount, bracket_max) - bracket_min)

        return margin * bracket_rate
