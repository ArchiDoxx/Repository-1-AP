from fastapi import FastAPI as fapi

app = fapi()

@app.get("/")
def root():
    return {"message": "Hello World"}


@app.get("/name/{name}")
def greet_name(name: str):
    return {"message": f"Hello {name}!"}



@app.get ("/add/{num1}/{num2}")
def add_numbers(num1: int, num2: int):
    result = num1 + num2
    return {"result": result}