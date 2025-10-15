from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db.connection import init_db
from .api.query import router as query_router
from .api.geojson import router as geojson_router


app = FastAPI()

# Allow the Vite frontend to call the API while blocking other origins.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    # Initialize database connections and other startup tasks.
    init_db()


# Attach the existing API routers (query + geojson endpoints).
app.include_router(query_router)
app.include_router(query_router)
app.include_router(geojson_router)


@app.get("/")
def home():
    # Simple heartbeat endpoint for service health checks.
    return {"message": "hi, City of Edmonton Traffic Volume System is running!"}
