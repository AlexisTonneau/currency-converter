import os

import uvicorn as uvicorn
from fastapi import FastAPI, HTTPException
from urllib.parse import unquote

import requests

app = FastAPI()

api_key = os.getenv('API_KEY')
countries = requests.get(
    'https://raw.githubusercontent.com/samayo/country-json/master/src/country-by-currency-code.json').json()


@app.get('/')
async def get_conversion(country: str, number: float):
    print(country)
    currency = None
    for ctr in countries:
        if ctr['country'] == country:
            currency = ctr['currency_code']
    if not currency:
        raise HTTPException(status_code=400, detail='Country not found')

    resp = requests.get(f'https://free.currconv.com/api/v7/convert?q={currency}_EUR&apiKey={api_key}&compact=ultra')
    if not resp.ok:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
    try:
        return str(round(float(resp.json()[f'{currency}_EUR'])*number, 2))
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=os.getenv('PORT') or 9000)
