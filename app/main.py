from fastapi import FastAPI

app = FastAPI(title="DOM API - Hello")

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}