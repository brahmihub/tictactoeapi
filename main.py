from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse

app = FastAPI()

pending_challenges = set()
active_games = {}

def get_empty_board():
    return ["1", "2", "3", "4", "5", "6", "7", "8", "9"]

def format_board(board):
    display = ""

    # First row
    display += f"|{board[0] if board[0] in ['❌', '⭕'] else '  ' + board[0]}|  {board[1] if board[1] in ['❌', '⭕'] else board[1]} |  {board[2] if board[2] in ['❌', '⭕'] else board[2]} |                                       \n"
    # Second row
    display += f"|  {board[3] if board[3] not in ['❌', '⭕'] else ' '} |  {board[4] if board[4] not in ['❌', '⭕'] else ' '} |  {board[5] if board[5] not in ['❌', '⭕'] else ' '} |                                        \n"
    # Third row
    display += f"|  {board[6] if board[6] not in ['❌', '⭕'] else ' '} |  {board[7] if board[7] not in ['❌', '⭕'] else ' '} |  {board[8] if board[8] not in ['❌', '⭕'] else ' '} |                        \n"

    display += "Choose one of the available numbers!"
    return display


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
