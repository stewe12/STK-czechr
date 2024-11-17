import asyncio
import aiohttp
import json
import os
from aiohttp import web
import logging

_LOGGER = logging.getLogger(__name__)

async def fetch_inspection_data(session, vin):
    """Fetch vehicle inspection data by VIN."""
    url = f"https://www.dataovozidlech.cz/api/Vozidlo/GetVehicleInfo?vin={vin}"
    async with session.get(url) as response:
        if response.status == 200:
            return await response.json()
        else:
            _LOGGER.error("Error fetching data for VIN %s: %s", vin, response.status)
            return {"error": f"Failed to fetch data for VIN {vin}. Status: {response.status}"}

async def handle(request):
    """Handle incoming requests to fetch inspection data for all cars."""
    cars = request.app['cars']
    if not cars:
        return web.json_response({"error": "No cars configured."}, status=400)

    tasks = []
    async with aiohttp.ClientSession() as session:
        for car in cars:
            tasks.append(fetch_inspection_data(session, car['vin']))
        results = await asyncio.gather(*tasks)

    response_data = {car['name']: result for car, result in zip(cars, results)}
    return web.json_response(response_data)

def load_cars():
    """Load car configuration from options.json."""
    try:
        with open('/data/options.json', 'r') as f:
            config = json.load(f)
            return config.get('cars', [])
    except FileNotFoundError:
        _LOGGER.warning("Configuration file not found. Using empty list.")
    except json.JSONDecodeError as e:
        _LOGGER.error("Error parsing configuration file: %s", e)
    return []

def create_app():
    """Create and configure the web application."""
    app = web.Application()
    app['cars'] = load_cars()
    app.router.add_get('/', handle)
    return app

# If running standalone
if __name__ == "__main__":
    app = create_app()
    web.run_app(app, port=8080)
