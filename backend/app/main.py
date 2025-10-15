from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "hi, City of Edmonton Traffic Volume System is running!"}
