from fastapi import APIRouter
from ..db.connection import execute_query

router = APIRouter(prefix="/query", tags=["Query"])

@router.get("/test")
def test_query():
    """Running a simple test query to check DB connectivity"""
    try:
        result = execute_query("SELECT 1 AS test;")
        return {"status": "success", "result": result}
    except Exception as e:
        return {"status": "error", "detail": str(e)}
