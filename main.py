from fastapi import FastAPI as fapi

app = fapi()

@app.get("/")
def root():
    return {"message": "Hello World"}