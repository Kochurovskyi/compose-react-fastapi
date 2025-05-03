import os
from fastapi import FastAPI, HTTPException, Body, Request
from fastapi.middleware.cors import CORSMiddleware
import redis
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

# Configuration from environment variables
redis_host = os.environ.get('REDIS_HOST', 'localhost')
redis_port = int(os.environ.get('REDIS_PORT', 6379))
pg_user = os.environ.get('PGUSER', 'postgres')
pg_host = os.environ.get('PGHOST', 'localhost')
pg_database = os.environ.get('PGDATABASE', 'postgres')
pg_password = os.environ.get('PGPASSWORD', 'postgres')
pg_port = int(os.environ.get('PGPORT', 5432))

# Set up FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(CORSMiddleware, allow_origins=["*"],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# PostgreSQL connection setup
def get_db_connection():
    conn = None
    try:
        # Set SSL mode based on environment
        if os.environ.get('ENVIRONMENT') != 'production':
            conn = psycopg2.connect(user=pg_user, host=pg_host,
                database=pg_database, password=pg_password, port=pg_port)
        else:
            conn = psycopg2.connect(user=pg_user, host=pg_host,
                database=pg_database, password=pg_password, port=pg_port, sslmode='require')
        # Create values table if it doesn't exist
        with conn.cursor() as cur:
            cur.execute('CREATE TABLE IF NOT EXISTS values (number INT)')
            conn.commit()
        return conn
    except Exception as e:
        print(f"<<<Database connection error: {e}>>>")
        if conn: conn.close()
        return None

# Redis connection setup
redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
# Create a duplicate Redis client for publishing
redis_publisher = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)

# Routes
@app.get("/")
def read_root(): return "<<< Hi, Can't believe in that - alive! >>>"

@app.get("/values/current")
def get_current_values():
    try:
        values = redis_client.hgetall('values')
        return values
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

class IndexInput(BaseModel): index: str


@app.post("/values")
async def add_value(request: Request):
    try:
        # Get the raw request body
        body = await request.body()
        print(f"Raw request body: {body}")

        # Parse the JSON
        try:
            data = json.loads(body)
            print(f"Parsed data: {data}")
            index = data.get('index')

            if not index:
                raise HTTPException(status_code=400, detail="Index is required")
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON")                                             # Check if index is too high
        if int(index) > 40: raise HTTPException(status_code=422, detail="Index too high")
        redis_client.hset('values', index, 'Nothing yet!')      # Store in Redis and publish to channel
        redis_publisher.publish('insert', index)
        conn = get_db_connection()                                          # Store in PostgreSQL
        if conn:
            with conn.cursor() as cur:
                cur.execute('INSERT INTO values(number) VALUES(%s)', (index,))
                conn.commit()
            conn.close()
        return {"working": True}
    except ValueError: raise HTTPException(status_code=400, detail="<<< Invalid index format >>>")
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))


@app.get("/values/all")
def get_all_values():
    conn = get_db_connection()
    if not conn: raise HTTPException(status_code=500, detail="Database connection failed")
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute('SELECT * FROM values')
            values = cur.fetchall()
        conn.close()
        return values
    except Exception as e:
        if conn:
            conn.close()
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=5000, reload=False)
