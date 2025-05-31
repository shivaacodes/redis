import os 
from fastapi import FastAPI 
from redis import Redis  
import httpx  
import json 

app = FastAPI()  

@app.on_event("startup")
async def startup_event():
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = int(os.getenv("REDIS_PORT", 6379))
    app.state.redis = Redis(host=redis_host, port=redis_port, decode_responses=True)
    app.state.http_client = httpx.AsyncClient()


@app.on_event("shutdown")
async def shutdown_event():
    app.state.redis.close()
    await app.state.http_client.aclose()


@app.get("/fact")
async def read_item():

    value = app.state.redis.get("fact")
    if value is not None:
        return json.loads(value)

    response = await app.state.http_client.get('https://catfact.ninja/fact')
    data = response.json()  

    app.state.redis.set("fact", json.dumps(data), ex=3600)
    return data
