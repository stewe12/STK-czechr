import asyncio
import aiohttp
import json
import os
from aiohttp import web

async def fetch_inspection_data(session, vin):
    url = f"https://www.dataovozidlech.cz/api/Vozidlo/GetVehicleInfo?vin={vin}"
    async with session.get(url) as response:
        return await response.json()

async def handle(request):
    cars = request.app['cars']
    tasks = []
    async with aiohttp.ClientSession() as session:
        for car in cars:
            tasks.append(fetch_inspection_data(session, car['vin']))
        results = await asyncio.gather(*tasks)
    
    response_data = {}
    for car, result in zip(cars, results):
        response_data[car['name']] = result
    
    return web.json_response(response_data)

def load_cars():
    if os.path.exists('/data/options.json'):
        with open('/data/options.json', 'r') as f:
            config = json.load(f)
            return config.get('cars', [])
    return []

app = web.Application()
app['cars'] = load_cars()
app.router.add_get('/', handle)

web.run_app(app, port=8080)
