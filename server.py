from fastapi import APIRouter, FastAPI
from pydantic import BaseModel
from database_chat import SQLAgent
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, Response
from io import BytesIO
import pandas as pd
from query_routes import router as query_router

class RequestBody(BaseModel):
    prompt: str
    
class ValidationResponse(BaseModel):
    is_valid:bool

class SuggestionsResponse(BaseModel):
    suggestion:str

class QueryResponse(BaseModel):
    query:str

class ErrorResponse(BaseModel):
    error:str

def configure_api_router(router:APIRouter,agent:SQLAgent)->APIRouter:
    """
    Given the router, configure paths
    """
    @router.get('/')
    def sanity_check():
        return {"Message":"Connection Works"}
    
    

    @router.post('/validate')
    def post_hander(request_body:RequestBody):
        
        try:
            is_valid = agent.validate_prompt_adequacy(request_body.prompt)
            response = ValidationResponse(is_valid=is_valid)
            jsonable_response = jsonable_encoder(response)
            return JSONResponse(content=jsonable_response)
        except Exception as e:
            error_response = ErrorResponse(error=str(e.args))
            jsonable_response = jsonable_encoder(error_response)
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
        try:
            df = agent.return_dataframe(request_body.prompt)
            excel_buffer = BytesIO()
            
            with pd.ExcelWriter(path=excel_buffer) as writer:
                df.to_excel(writer,index=False)
            
            excel_buffer.seek(0)
            headers = {'Content-Disposition': 'attachment; filename="Book.xlsx"'}
            media_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            return Response(content=excel_buffer.getvalue(),headers=headers,media_type=media_type)
        except Exception as e:
            error_response = ErrorResponse(error=str(e.args))
            jsonable_response = jsonable_encoder(error_response)
            return JSONResponse(content=jsonable_response)
    
    return router



agent = SQLAgent()
app = FastAPI()
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # Frontend origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = configure_api_router(APIRouter(),agent)
app.include_router(router=router)
app.include_router(query_router)
