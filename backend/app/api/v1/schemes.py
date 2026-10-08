from fastapi import APIRouter, HTTPException
from app.services.content.schemes_data import SEED_SCHEMES

router = APIRouter(prefix="/schemes", tags=["government-schemes"])


@router.get("/")
def list_schemes():
    return [{"slug": s.slug, "name": s.name, "overview": s.overview} for s in SEED_SCHEMES]


@router.get("/{slug}")
def get_scheme(slug: str):
    scheme = next((s for s in SEED_SCHEMES if s.slug == slug), None)
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")
    return scheme
