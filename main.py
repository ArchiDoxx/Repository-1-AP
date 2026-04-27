from fastapi import FastAPI as fapi

app = fapi()

@app.get("/")
def root():
    return {"message": "Hello World"}


@app.get("/name/{name}")
def greet_name(name: str):
    return {"message": f"Hello {name}!"}
