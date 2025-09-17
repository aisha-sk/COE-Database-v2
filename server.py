from fastapi import APIRouter, FastAPI
from pydantic import BaseModel
from database_chat import SQLAgent

class PromptBody(BaseModel):
    prompt: str
    stage: int

def configure_api_router(router:APIRouter)->APIRouter:
    """
    Given the router, configure paths
    """
    @router.get('/')
    def sanity_check():
        return {"Message":"Connection Works"}
    
    

    @router.post('/')
    def post_hander(request_body:PromptBody):
        print(request_body.prompt,request_body.stage)
    
    return router
    

app = FastAPI()
router = configure_api_router(APIRouter())

app.include_router(router=router)