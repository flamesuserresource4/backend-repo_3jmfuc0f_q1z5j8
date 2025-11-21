from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any, Dict

from database import db
import schemas as app_schemas

app = FastAPI(title="PEEUSH Portfolio API", version="1.0.0")

# CORS for local dev and modal preview domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root() -> Dict[str, Any]:
    return {"status": "ok", "service": "portfolio-backend"}


@app.get("/health")
def health() -> Dict[str, Any]:
    return {"ok": True}


@app.get("/test")
def test_connection() -> Dict[str, Any]:
    try:
        if db is None:
            raise RuntimeError("Database not configured")
        # Basic ping to Mongo
        result = db.command("ping")
        return {"database": "ok", "result": result}
    except Exception as e:
        # Return error detail but keep 200 so platform health check can still reach endpoint
        return {"database": "error", "detail": str(e)}


# Expose schemas so the platform viewer can read them
@app.get("/schema")
def get_schema() -> Dict[str, Any]:
    models = {}
    for name in dir(app_schemas):
        obj = getattr(app_schemas, name)
        if isinstance(obj, type) and issubclass(obj, BaseModel) and obj is not BaseModel:
            try:
                models[name] = obj.model_json_schema()
            except Exception:
                # Fallback minimal description
                models[name] = {"title": name}
    return {"models": models}


# Optional: simple echo endpoint useful for quick tests
class EchoIn(BaseModel):
    message: str


@app.post("/echo")
def echo(payload: EchoIn) -> Dict[str, str]:
    return {"echo": payload.message}
