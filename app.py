import json
import os
import time
import shutil

import requests_cache
import instaloader
import uvicorn as uvicorn
from fastapi import FastAPI, HTTPException, Response

import requests
from starlette.background import BackgroundTasks
from starlette.responses import FileResponse

app = FastAPI()
ig = instaloader.Instaloader(dirname_pattern="./insta/{target}")

api_key_currconv = os.getenv('API_KEY_CURRCONV')
api_key_freecurrency = os.getenv('API_KEY_FREECURRENCY')

requests_cache.install_cache('currency_cache', backend='sqlite', expire_after=60 * 60 * 24)


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

    try:
        return Response(content=str(get_rates(currency, native_currency, number)),
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

    print(get_rates(currency, native_currency, number))

    try:
        return Response(content=str(get_rates(currency, native_currency, number)) +
                                complete_curr[native_currency]['symbol_native'],
                        media_type="text"
                                   "/plain")
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)


@app.get("/insta/{insta_profile}")
async def root(insta_profile: str, background_tasks: BackgroundTasks):
    ig.download_profile(insta_profile, profile_pic_only=True)
    path = f"./insta/{insta_profile}/"
    final_path = None
    for file in os.listdir(path):
        if file.endswith(".jpg"):
            final_path = os.path.join(path, file)
    background_tasks.add_task(delete_folder, path)
    return FileResponse(final_path)


def get_rates(currency, native_currency, number):
    resp = requests.get(
        f'https://free.currconv.com/api/v7/convert?q={currency}_{native_currency}&apiKey={api_key_currconv}&compact=ultra')
    if not resp.ok:
        print("currconv failed")
        resp = requests.get(
            f'https://freecurrencyapi.net/api/v2/latest?apiKey={api_key_freecurrency}&base_currency={native_currency}')
        if not resp.ok:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
        return round(number / float(resp.json()['data'][currency]), 2)
    else:
        return round(number / float(resp.json()[f'{currency}_{native_currency}']), 2)


def delete_folder(path):
    time.sleep(4)
    if os.path.exists(path):
        shutil.rmtree(path)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=os.getenv('PORT') or 9000)
