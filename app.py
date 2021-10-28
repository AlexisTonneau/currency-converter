import json
import os

import uvicorn as uvicorn
from fastapi import FastAPI, HTTPException, Response

import requests

app = FastAPI()

api_key = os.getenv('API_KEY')
with open('country-by-currency-code.json') as f:
    countries = json.load(f)

with open('Common-Currency.json') as f:
    complete_curr = json.load(f)

for ctr in countries:
    if ctr['country'] == 'France':
        assert ctr['currency_code'] == 'EUR'

currencies = []

for ctr in countries:
    currencies.append(ctr['currency_code'])


@app.get('/')
async def get_conversion(country: str, number: float, native_currency: str = 'EUR'):
    native_currency = native_currency.upper()
    if native_currency not in currencies:
        return Response(media_type="text/plain", content=f"{native_currency} not recognized")
    currency = None
    for ctr in countries:
        if ctr['country'] == country:
            currency = ctr['currency_code']
    if not currency:
        return Response(media_type="text/plain", content=f"{country} not recognized")

    resp = requests.get(
        f'https://free.currconv.com/api/v7/convert?q={currency}_{native_currency}&apiKey={api_key}&compact=ultra')
    if not resp.ok:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
    try:
        return Response(content=str(round(float(resp.json()[f'{currency}_{native_currency}']) * number, 2)),
                        media_type="text"
                                   "/plain")
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)


@app.get('/1.4')
async def get_conversion(country: str, number: float, native_currency: str = 'EUR'):
    native_currency = native_currency.upper()
    if native_currency not in currencies:
        return Response(media_type="text/plain", content=f"{native_currency} not recognized")
    currency = None
    for ctr in countries:
        if ctr['country'] == country:
            currency = ctr['currency_code']
    if not currency:
        return Response(media_type="text/plain", content=f"{country} not recognized")

    resp = requests.get(
        f'https://free.currconv.com/api/v7/convert?q={currency}_{native_currency}&apiKey={api_key}&compact=ultra')
    if not resp.ok:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
    try:
        return Response(content=str(round(float(resp.json()[f'{currency}_{native_currency}']) * number, 2)) +
                                complete_curr[native_currency]['symbol_native'],
                        media_type="text"
                                   "/plain")
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=os.getenv('PORT') or 9000)
