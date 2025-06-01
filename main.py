from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse

app = FastAPI()

@app.get("/tac")
async def tac_command(request: Request):
    caller = request.query_params.get("user") or "someone"
    target = request.query_params.get("query")

    if not target:
        return PlainTextResponse(f"@{caller}, tag someone to play!")

    return PlainTextResponse(f"@{caller} vs {target} — let the game begin!")
