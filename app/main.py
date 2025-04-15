from fastapi import FastAPI

from app.controllers import fetch_tax_brackets
from app.models.tax_calculator_request import TaxCalculatorRequest

app = FastAPI()


@app.post("/")
def tax_calculator(tax_calculator_request: TaxCalculatorRequest):
    """Tax calculator route."""

    tax_brackets = fetch_tax_brackets(tax_calculator_request.tax_year)

    total_tax, effective_tax_rate, marginal_taxes = tax_brackets.compute_tax(
        tax_calculator_request.yearly_salary,
    )

    return {
        "total_tax": total_tax,
        "effective_tax_rate": effective_tax_rate,
        "marginal_taxes": marginal_taxes,
        "tax_brackets": tax_brackets.tax_brackets,
    }
