from fastapi import FastAPI

app = FastAPI(title="CAD Yield Curve API")

@app.get("/")
def health_check():
    return {"status": "ok", "message": "CAD Yield Curve API is running"}