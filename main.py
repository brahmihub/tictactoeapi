from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse

app = FastAPI()

pending_challenges = set()
active_games = {}

def get_empty_board():
    
    return ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]

def format_board(board):
    # Format each cell with spaces (e.g. " 1 ", " ❌ ", etc.)
    formatted = [
        f"{cell}" if cell in ["❌", "⭕"] else f"{cell}" for cell in board
    ]

    # Create rows
    rows = []
    for i in range(0, 9, 3):
        row = "|".join(formatted[i:i+3])
        rows.append(row)

    # Join rows with a visible separator (you can change this)
    return ''.join(row + "................................................................" for row in rows)


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

        # Check for win
        wins = [(0,1,2), (3,4,5), (6,7,8),
                (0,3,6), (1,4,7), (2,5,8),
                (0,4,8), (2,4,6)]
        if any(board[a] == board[b] == board[c] == symbol for a, b, c in wins):
            del active_games[user_game]
            return PlainTextResponse(
                f"@{user} wins!\n\n{format_board(board)}"
            )

        # Check for draw
        if all(cell in ["❌", "⭕"] for cell in board):
            del active_games[user_game]
            return PlainTextResponse(
                f"It's a draw!\n\n{format_board(board)}"
            )

        next_turn = user_game[0] if user == user_game[1] else user_game[1]
        game["turn"] = next_turn
        return PlainTextResponse(
            f"-------------------------------{format_board(board)} @{user} made a move!, @{next_turn}, it's your turn!"
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
            f"GAME STARTED!-----------{format_board(board)} @{user} vs @{target} — @{player1}, you're ❌ — go first!"
        )
    else:
        pending_challenges.add(pair)
        return PlainTextResponse(
            f"@{user} vs @{target} — Tic Tac Toe challenge sent!\n"
            f"@{target}, type !tac {user} to accept."
        )
