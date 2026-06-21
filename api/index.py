from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import json
import numpy as np
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

BASE_DIR = os.path.dirname(__file__)
DATA_PATH = os.path.join(BASE_DIR, "q-vercel-latency.json")

with open(DATA_PATH, "r") as f:
    data = json.load(f)

@app.post("/")
async def analyze(request: Request):
    body = await request.json()
    regions = body["regions"]
    threshold = body["threshold_ms"]

    result = {}

    for region in regions:
        rows = [r for r in data if r["region"] == region]

        lat = [r["latency_ms"] for r in rows]
        up = [r["uptime_pct"] for r in rows]

        result[region] = {
            "avg_latency": sum(lat) / len(lat),
            "p95_latency": float(np.percentile(lat, 95)),
            "avg_uptime": sum(up) / len(up),
            "breaches": sum(1 for r in rows if r["latency_ms"] > threshold)
        }

    return result