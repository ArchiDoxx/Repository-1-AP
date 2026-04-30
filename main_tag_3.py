from fastapi import FastAPI as fapi

app = fapi()

@app.get("/queryparameters")
def get_query_parameters(param1: str, param2: int) -> dict:
        return {"param1": param1, "param2": param2}