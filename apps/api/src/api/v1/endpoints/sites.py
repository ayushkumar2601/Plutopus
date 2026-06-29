from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from plutopus_shared import get_db, Site
from schemas.api_models import SiteSchema

router = APIRouter()

@router.get("/", response_model=List[SiteSchema])
def get_sites(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Retrieve all seeded network sites with pagination.
    """
    sites = db.query(Site).offset(skip).limit(limit).all()
    return sites
