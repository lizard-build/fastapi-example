from fastapi import FastAPI

app = FastAPI(title="FastAPI deployment example")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/echo")
def echo(payload: dict):
    return {"echo": payload}
