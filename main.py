from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse

app = FastAPI()

# In-memory data
pending_challenges = set()
active_games = {}  # { (player1, player2): { "board": [...], "turn": "player1", "symbols": {player1: ❌, player2: ⭕} } }

def get_empty_board():
    return ["1", "2", "3", "4", "5", "6", "7", "8", "9"]

def format_board(board):
    return f"|{board[0]}|{board[1]}|{board[2]}|\n|{board[3]}|{board[4]}|{board[5]}|\n|{board[6]}|{board[7]}|{board[8]}|"

@app.get("/tac")
async def tac_command(request: Request):
    user = request.query_params.get("user", "").lstrip("@").lower()
    query = request.query_params.get("query", "").strip().lower()

    if not query:
        return PlainTextResponse(f"@{user}, tag someone or use !tac [1-9] to make a move.")

    # If query is a digit between 1-9, it's a move
    if query.isdigit() and query in "123456789":
        move = int(query)
        for pair, game in active_games.items():
            if user in pair:
                current_turn = game["turn"]
                if user != current_turn:
                    return PlainTextResponse(f"@{user}, it's not your turn!")
                board = game["board"]
                if board[move - 1] in ["❌", "⭕"]:
                    return PlainTextResponse(f"@{user}, that spot is already taken!")
                symbol = game["symbols"][user]
                board[move - 1] = symbol
                # Switch turn
                next_turn = pair[0] if user == pair[1] else pair[1]
                game["turn"] = next_turn
                return PlainTextResponse(
                    f"@{user} made a move!\n\n{format_board(board)}\n\n@{next_turn}, it's your turn!"
                )
        return PlainTextResponse(f"@{user}, you're not in a game. Start one with !tac @username")

    # Otherwise, it's a challenge
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
        symbols = {user: "❌", target: "⭕"} if user < target else {user: "⭕", target: "❌"}
        active_games[pair] = {
            "board": board,
            "turn": player1,  # First turn always goes to the alphabetically first user
            "symbols": symbols
        }
        return PlainTextResponse(
            f"@{user} vs @{target} — Game started!\n\n{format_board(board)}\n\n@{player1}, you're ❌ — go first!"
        )
    else:
        pending_challenges.add(pair)
        return PlainTextResponse(
            f"@{user} vs @{target} — Tic Tac Toe challenge sent!\n"
            f"@{target}, type !tac {user} to accept."
        )
