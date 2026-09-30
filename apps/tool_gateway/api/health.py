from fastapi import APIRouter

router = APIRouter(tags=["Health"])

@router.get("/health")
async def healthz():
    return {"status": "ok", "service": "tool-gateway"}

@router.get("/ready")
async def ready():
    return {"status": "ready"}