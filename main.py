from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse

app = FastAPI()

games = {}

def format_board(board):
    # Formats the board exactly how the user wants for Twitch
    line1 = f"|{board[0]}|  {board[1]} |  {board[2]} |                                       \n"
    line2 = f"|  {board[3]} |  {board[4]} |  {board[5]} |                                        \n"
    line3 = f"|  {board[6]} |  {board[7]} |  {board[8]} |                        \n"
    return f"{line1}{line2}{line3}Choose one of the available numbers!"

def create_new_board():
    return ["1", "2", "3", "4", "5", "6", "7", "8", "9"]

@app.get("/", response_class=PlainTextResponse)
async def root(request: Request):
    args = request.query_params
    user = args.get("user", "").strip("@").lower()
    message = args.get("message", "").strip()

    if not message:
        return "Please provide a command."

    parts = message.split()
    command = parts[0].lower()

    # Challenge someone or make move
    if command == "!tac":
        if len(parts) == 2 and parts[1].isdigit():  # Player making a move
            move = parts[1]
            # Find game where user is playing
            for game_id, game in games.items():
                if user in [game["player1"], game["player2"]]:
                    if not game.get("accepted"):
                        return f"@{user}, your challenge hasn't been accepted yet."
                    if game["turn"] != user:
                        return f"@{user}, it's not your turn!"
                    if move not in game["board"]:
                        return f"@{user}, invalid move! Position {move} is not available."
                    index = game["board"].index(move)
                    game["board"][index] = game["symbols"][user]
                    board_str = format_board(game["board"])

                    # Check for win
                    b = game["board"]
                    s = game["symbols"][user]
                    wins = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
                    if any(b[a]==b[b_]==b[c]==s for a,b_,c in wins):
                        games.pop(game_id)
                        return f"@{user} made a move!\n{board_str}\n@{user} wins the game! 🎉"

                    # Check draw
                    if all(pos in ['❌', '⭕'] for pos in game["board"]):
                        games.pop(game_id)
                        return f"@{user} made a move!\n{board_str}\nIt's a draw!"

                    # Switch turn
                    other = game["player2"] if game["turn"] == game["player1"] else game["player1"]
                    game["turn"] = other
                    return f"@{user} made a move!\n{board_str}\n@{other}, it's your turn!"

            return f"@{user}, you are not currently in a game!"

        elif len(parts) == 2:  # Challenge another player or accept challenge
            opponent = parts[1].strip("@").lower()
            if opponent == user:
                return f"@{user}, you can't challenge yourself. Tag someone else."

            game_id = tuple(sorted([user, opponent]))

            # Check if game exists between these two
            if game_id in games:
                game = games[game_id]
                if not game.get("accepted"):
                    # Check if this is acceptance (user accepts challenge from opponent)
                    if user != game["player1"]:  # only second player accepts
                        game["accepted"] = True
                        game["turn"] = game["player1"]  # player1 starts
                        board_str = format_board(game["board"])
                        p1, p2 = game["player1"], game["player2"]
                        return f"Match started between @{p1} (❌) and @{p2} (⭕)!\n{board_str}\n@{p1}, it's your turn!"
                    else:
                        return f"@{user}, you sent the challenge, waiting for @{opponent} to accept."
                else:
                    return f"@{user}, you're already in a game with @{opponent}!"

            # Start new challenge
            games[game_id] = {
                "player1": user,
                "player2": opponent,
                "board": create_new_board(),
                "accepted": False,
                "symbols": {user: "❌", opponent: "⭕"},
                "turn": None,
            }
            return f"@{user} vs @{opponent} — Tic Tac Toe challenge sent!\n@{opponent}, type !tac {user} to accept."

        else:
            return f"@{user}, tag someone to start a Tic Tac Toe game."

    return "Unknown command."
