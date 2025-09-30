from fastapi import APIRouter, FastAPI
from pydantic import BaseModel
from database_chat import SQLAgent
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, Response
from io import BytesIO
import pandas as pd

class RequestBody(BaseModel):
    prompt: str
    
class ValidationResponse(BaseModel):
    is_valid:bool

class SuggestionsResponse(BaseModel):
    suggestion:str

class QueryResponse(BaseModel):
    query:str

def configure_api_router(router:APIRouter,agent:SQLAgent)->APIRouter:
    """
    Given the router, configure paths
    """
    @router.get('/')
    def sanity_check():
        return {"Message":"Connection Works"}
    
    

    @router.post('/validate')
    def post_hander(request_body:RequestBody):
        
        is_valid = agent.validate_prompt_adequacy(request_body.prompt)
        response = ValidationResponse(is_valid=is_valid)
        jsonable_response = jsonable_encoder(response)
        return JSONResponse(content=jsonable_response)
    
    @router.post('/suggestion')
    def post_handler(request_body:RequestBody):
        suggestion = agent.generate_prompt_suggestions(request_body.prompt)
        response = SuggestionsResponse(suggestion=suggestion)
        jsonable_response = jsonable_encoder(response)
        return JSONResponse(content=jsonable_response)
    
    @router.post('/query')
    def post_hander(request_body:RequestBody):
        query = agent.generate_query(request_body.prompt)
        response = QueryResponse(query=query)
        jsonable_response = jsonable_encoder(response)
        return JSONResponse(content=jsonable_response)
    
    @router.post('/excel_file')
    def post_handler(request_body:RequestBody):
        df = agent.return_dataframe(request_body.prompt)
        excel_buffer = BytesIO()
        
        with pd.ExcelWriter(path=excel_buffer) as writer:
            df.to_excel(writer,index=False)
        
        excel_buffer.seek(0)
        headers = {'Content-Disposition': 'attachment; filename="Book.xlsx"'}
        media_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        return Response(content=excel_buffer.getvalue(),headers=headers,media_type=media_type)
    
    return router

if __name__ == "__main__":
    agent = SQLAgent()
    app = FastAPI()
    router = configure_api_router(APIRouter(),agent)
    app.include_router(router=router)
    
    import uvicorn
    uvicorn.run(app,host="0.0.0.0",port=8000)