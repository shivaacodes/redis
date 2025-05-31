import os 
from fastapi import FastAPI 
from redis import Redis  
import httpx  
import json 

app = FastAPI()  


@app.on_event("startup")
async def startup_event():
    """
    This function runs once when the FastAPI app starts up.
    It sets up resources that will be used during the app's lifetime,
    such as Redis client and HTTP client, and stores them in app.state
    for shared access across requests.
    """

    # Read Redis host from environment variable or default to 'localhost'
    redis_host = os.getenv("REDIS_HOST", "localhost")
    # Read Redis port from environment variable or default to 6379 (default Redis port)
    redis_port = int(os.getenv("REDIS_PORT", 6379))

    # Initialize Redis client connection with given host, port,
    # and decode_responses=True to automatically decode bytes to string
    app.state.redis = Redis(host=redis_host, port=redis_port, decode_responses=True)

    # Initialize an asynchronous HTTP client to make non-blocking API calls
    app.state.http_client = httpx.AsyncClient()


@app.on_event("shutdown")
async def shutdown_event():
    """
    This function runs once when the FastAPI app is shutting down.
    It properly closes the Redis connection and the HTTP client to free up resources.
    """

    # Close the Redis connection cleanly
    app.state.redis.close()
    # Asynchronously close the HTTP client session to avoid resource leaks
    await app.state.http_client.aclose()


@app.get("/currencies")
async def read_item():
    """
    GET endpoint '/currencies' which:
    - Checks if currency data is cached in Redis and returns it if available.
    - If not cached, fetches the data from Coinbase API, stores it in Redis cache,
      and then returns it.
    """

    # Try to get cached currency data from Redis using the key 'currencies'
    value = app.state.redis.get("currencies")

    # If cached data exists in Redis, parse it from JSON string back to Python dict and return
    if value is not None:
        return json.loads(value)

    # If not cached, make an async GET request to Coinbase API to fetch latest currency data
    response = await app.state.http_client.get('https://api.coinbase.com/v2/currencies')
    data = response.json()  # Parse response JSON into Python dictionary

    # Cache the fetched data in Redis as a JSON string with an expiry of 1 hour (3600 seconds)
    # This improves performance by avoiding repeated external API calls within expiry time
    app.state.redis.set("currencies", json.dumps(data), ex=3600)

    # Return the freshly fetched currency data as API response
    return data
