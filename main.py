from fastapi import FastAPI
from redis import Redis
import httpx
import json

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    app.state.redis = Redis(host='localhost', port=6379, decode_responses=True)
    app.state.http_client = httpx.AsyncClient()

@app.on_event("shutdown")
async def shutdown_event():
    app.state.redis.close()
    await app.state.http_client.aclose()

@app.get("/currencies")
async def read_item():
    value = app.state.redis.get("currencies")
    if value is not None:
        # Return cached value
        return json.loads(value)

    # If not cached, fetch from API
    response = await app.state.http_client.get('https://api.coinbase.com/v2/currencies')
    data = response.json()

    # Cache it in Redis as a string
    app.state.redis.set("currencies", json.dumps(data), ex=3600)  # optional expiry (1 hour)

    return data
