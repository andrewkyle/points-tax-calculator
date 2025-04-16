from decimal import Decimal

from pydantic import BaseModel


class TaxCalculatorRequest(BaseModel):
    """A model used to represent a tax calculator request."""

    tax_year: int
    yearly_salary: Decimal
