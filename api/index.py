from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np
import json
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

file_path = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "q-vercel-latency.json"
)

with open(file_path, "r", encoding="utf-8") as f:
    data = json.load(f)

df = pd.DataFrame(data)

class RequestBody(BaseModel):
    regions: list[str]
    threshold_ms: float

@app.options("/{rest_of_path:path}")
async def preflight_handler(rest_of_path: str):
    response = Response()
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

@app.post("/")
def latency_metrics(req: RequestBody):
    result = {}

    for region in req.regions:
        region_df = df[df["region"] == region]

        result[region] = {
            "avg_latency": float(region_df["latency_ms"].mean()),
            "p95_latency": float(np.percentile(region_df["latency_ms"], 95)),
            "avg_uptime": float(region_df["uptime_pct"].mean()),
            "breaches": int(
                (region_df["latency_ms"] > req.threshold_ms).sum()
            )
        }

    return result