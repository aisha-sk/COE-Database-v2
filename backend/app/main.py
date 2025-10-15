from fastapi import FastAPI
from .db.connection import init_db
from .api.query import router as query_router
from .api.geojson import router as geojson_router


app = FastAPI()

@app.on_event("startup")
def startup_event():
    init_db()
app.include_router(query_router)
app.include_router(query_router)
app.include_router(geojson_router)

@app.get("/")
def home():
    return {"message": "hi, City of Edmonton Traffic Volume System is running!"}
