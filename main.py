from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse

app = FastAPI()

# In-memory data
pending_challenges = set()
active_games = {}

# Board template
def get_board():
    return "|1|2|3|\n|4|5|6|\n|7|8|9|"

@app.get("/tac")
async def tac_command(request: Request):
    caller = request.query_params.get("user", "").lstrip("@").lower()
    target = request.query_params.get("query", "").strip().lstrip("@").lower()

    if not target:
        return PlainTextResponse(f"@{caller}, tag someone to play!")

    if caller == target:
        return PlainTextResponse(f"@{caller}, you can't play against yourself!")

    pair = tuple(sorted([caller, target]))

    if pair in active_games:
        return PlainTextResponse(f"A game is already in progress between @{caller} and @{target}!")

    if pair in pending_challenges:
        pending_challenges.remove(pair)
        active_games[pair] = get_board()
        board = get_board()
        return PlainTextResponse(
            f"@{caller} vs @{target} — Game started!\n\n{board}"
        )
    else:
        pending_challenges.add(pair)
        return PlainTextResponse(
            f"@{caller} vs @{target} — Tic Tac Toe challenge sent!\n"
            f"@{target}, type !tac {caller} to accept."
        )
