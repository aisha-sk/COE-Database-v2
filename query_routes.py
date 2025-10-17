from pathlib import Path
from typing import Optional

import pandas as pd
from fastapi import APIRouter, HTTPException, Query

DATA_PATH = Path(__file__).resolve().parent / "data" / "sample_studies.csv"

router = APIRouter(prefix="/query", tags=["traffic-studies"])


@router.get("/studies")
def get_studies(
    start_year: int = Query(..., description="First year to include"),
    end_year: int = Query(..., description="Last year to include"),
    direction: Optional[str] = Query(
        None,
        description="Direction filter (e.g., Northbound). Use 'All' or omit to include every direction.",
    ),
):
    if start_year > end_year:
        raise HTTPException(status_code=400, detail="start_year must be less than or equal to end_year")

    try:
        df = pd.read_csv(DATA_PATH)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=f"Dataset not found at {DATA_PATH}") from exc
    except pd.errors.ParserError as exc:
        raise HTTPException(status_code=500, detail="Failed to parse sample_studies.csv") from exc

    filtered = df[(df["year"] >= start_year) & (df["year"] <= end_year)]

    if direction and direction.lower() != "all":
        filtered = filtered[filtered["direction"].str.lower() == direction.lower()]

    features = []
    for _, row in filtered.iterrows():
        try:
            lat = float(row["lat"])
            lon = float(row["lon"])
        except (TypeError, ValueError):
            # Skip rows that do not have valid coordinates
            continue

        feature = {
            "type": "Feature",
            "properties": {
                "id": row["id"],
                "year": int(row["year"]),
                "direction": row["direction"],
                "lat": lat,
                "lon": lon,
            },
            "geometry": {
                "type": "Point",
                "coordinates": [lon, lat],
            },
        }
        features.append(feature)

    return {"type": "FeatureCollection", "features": features}
