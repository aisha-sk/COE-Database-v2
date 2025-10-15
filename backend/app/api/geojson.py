from fastapi import APIRouter
from fastapi.responses import FileResponse, StreamingResponse, JSONResponse
import os, json

router = APIRouter(prefix="/geojson", tags=["GeoJSON"])
BASE = os.path.join(os.getcwd(), "data")

def file_path(layer: str):
    return os.path.join(BASE, f"{layer}.geojson")

@router.get("/{layer}")
def get_geojson(layer: str):
    """Return GeoJSON layers efficiently."""
    path = file_path(layer)
    if not os.path.exists(path):
        return JSONResponse({"error": f"{layer}.geojson not found"}, status_code=404)

    size = os.path.getsize(path)
    # Serve large file as stream, smaller ones as JSON
    if size > 10_000_000:  # 10 MB threshold
        def iterfile():
            with open(path, "rb") as f:
                yield from f
        return StreamingResponse(iterfile(), media_type="application/geo+json")
    else:
        with open(path) as f:
            return JSONResponse(json.load(f))
