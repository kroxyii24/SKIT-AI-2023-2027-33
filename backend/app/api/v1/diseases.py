from fastapi import APIRouter, HTTPException
from app.services.content.disease_data import SEED_DISEASES

router = APIRouter(prefix="/diseases", tags=["disease-awareness"])


@router.get("/")
def list_diseases(category: str | None = None):
    diseases = SEED_DISEASES
    if category:
        diseases = [d for d in diseases if d.category == category]
    return [{"slug": d.slug, "name": d.name, "category": d.category} for d in diseases]


@router.get("/{slug}")
def get_disease(slug: str):
    disease = next((d for d in SEED_DISEASES if d.slug == slug), None)
    if not disease:
        raise HTTPException(status_code=404, detail="Disease information not found")
    return disease
