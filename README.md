# Tax Calculator - Technical Assessment

First, start the dockerized API according to [the documentation provided by Points](https://github.com/points/interview-test-server).

Install runtime dependencies with `pipenv`:
```shell
pipenv install
```

Install runtime and development dependencies with `pipenv`:
```shell
pipenv install
```

Run development server:
```shell
fastapi dev app/main.py
```

Run tests:
```shell
pytest
```

Configure the app with a `.env`:
```shell
TAX_YEAR_URL="http://localhost:5001/tax-calculator/tax-year/{tax_year}"
TAX_YEAR_RETRY=5
TAX_YEAR_TIMEOUT=7
```
