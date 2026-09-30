from fastapi import FastAPI

health_app = FastAPI()

@health_app.get("/healthz")
async def healthz():
    return {"status": "ok", "service": "tool_gateway"}

@health_app.get("/ready")
async def ready():
    return {"status": "ready"}