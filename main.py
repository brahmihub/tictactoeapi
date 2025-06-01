from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse

app = FastAPI()

pending_challenges = set()
active_games = {}

def get_empty_board():
    return ["1", "2", "3", "4", "5", "6", "7", "8", "9"]

def format_board(board):
    # Top row with symbols (❌, ⭕, or blank)
    symbol_row = ""
    for i, cell in enumerate(board):
        symbol = cell if cell in ["❌", "⭕"] else " "
        symbol_row += f"|{symbol}"
        if (i + 1) % 3 == 0:
            symbol_row += "|\n"

    # Spacer row and numbered row
    numbered_row = ""
    for i, cell in enumerate(board):
        if cell not in ["❌", "⭕"]:
            numbered_row += f"|  {cell} "
        else:
            numbered_row += "|     "
        if (i + 1) % 3 == 0:
            numbered_row += "|\n"

    return f"{symbol_row}{numbered_row}Choose one of the available numbers!"

@app.get("/tac")
async def tac_command(request: Request):
    user = request.query_params.get("user", "").lstrip("@").lower()
    query = request.query_params.get("query", "").strip().lower()

    if not query:
        return PlainTextResponse(f"@{user}, tag someone or use !tac [1-9] to make a move.")

    # Check if user is in a game
    user_game = None
    for pair in active_games:
        if user in pair:
            user_game = pair
            break

    # If in a game, treat input as move
    if user_game:
        if query not in "123456789":
            return PlainTextResponse(f"@{user}, you're in a game. Use !tac [1-9] to make a move.")
        move = int(query)
        game = active_games[user_game]
        if user != game["turn"]:
            return PlainTextResponse(f"@{user}, it's not your turn!")
        board = game["board"]
        if board[move - 1] in ["❌", "⭕"]:
            return PlainTextResponse(f"@{user}, that spot is already taken!")
        symbol = game["symbols"][user]
        board[move - 1] = symbol
        next_turn = user_game[0] if user == user_game[1] else user_game[1]
        game["turn"] = next_turn
        return PlainTextResponse(
            f"@{user} made a move!\n\n{format_board(board)}\n@{next_turn}, it's your turn!"
        )

    # Not in a game → handle as challenge
    target = query.lstrip("@")
    if target == user:
        return PlainTextResponse(f"@{user}, you can't play against yourself!")

    pair = tuple(sorted([user, target]))

    if pair in active_games:
        return PlainTextResponse(f"A game is already in progress between @{pair[0]} and @{pair[1]}!")

    if pair in pending_challenges:
        pending_challenges.remove(pair)
        board = get_empty_board()
        player1, player2 = pair
        symbols = {player1: "❌", player2: "⭕"}
        active_games[pair] = {
            "board": board,
            "turn": player1,
            "symbols": symbols
        }
        return PlainTextResponse(
            f"@{user} vs @{target} — Game started!\n\n{format_board(board)}\n@{player1}, you're ❌ — go first!"
        )
    else:
        pending_challenges.add(pair)
        return PlainTextResponse(
            f"@{user} vs @{target} — Tic Tac Toe challenge sent!\n"
            f"@{target}, type !tac {user} to accept."
        )
