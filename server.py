from fastapi import APIRouter, FastAPI
from pydantic import BaseModel


def configure_api_router(router:APIRouter)->APIRouter:
    """
    Given the router, configure paths
    """
    @router.get('/')
    def sanity_check():
        return {"Message":"Connection Works"}
    
    return router
    

app = FastAPI()
router = configure_api_router(APIRouter())

app.include_router(router=router)