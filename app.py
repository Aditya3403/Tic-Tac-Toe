from flask import Flask, render_template, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins="*")

# Game variables
AI_PLAYER = 'O'
HUMAN_PLAYER = 'X'
board = [None] * 9

def minimax(board, depth, is_maximizing):
    if check_winner(board, AI_PLAYER):
        return 10 - depth
    if check_winner(board, HUMAN_PLAYER):
        return depth - 10
    if is_board_full(board):
        return 0

    best_score = -float('inf') if is_maximizing else float('inf')

    for i in range(9):
        if board[i] is None:
            board[i] = AI_PLAYER if is_maximizing else HUMAN_PLAYER
            score = minimax(board, depth + 1, not is_maximizing)
            board[i] = None
            best_score = max(best_score, score) if is_maximizing else min(best_score, score)

    return best_score

def get_best_move(board):
    best_score = -float('inf')
    best_move = -1

    for i in range(9):
        if board[i] is None:
            board[i] = AI_PLAYER
            score = minimax(board, 0, False)
            board[i] = None
            if score > best_score:
                best_score = score
                best_move = i

    return best_move

def check_winner(board, player):
    win_patterns = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],
        [0, 3, 6], [1, 4, 7], [2, 5, 8], 
        [0, 4, 8], [2, 4, 6]             
    ]
    return any(all(board[i] == player for i in pattern) for pattern in win_patterns)

def is_board_full(board):
    return all(cell is not None for cell in board)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/make_move', methods=['POST'])
def make_move():
    global board
    move = int(request.json['move']) 
    if board[move] is None:
        board[move] = HUMAN_PLAYER
        if check_winner(board, HUMAN_PLAYER):
            return jsonify({'status': 'win', 'board': board})
        if is_board_full(board):
            return jsonify({'status': 'draw', 'board': board})

        ai_move = get_best_move(board)
        board[ai_move] = AI_PLAYER
        if check_winner(board, AI_PLAYER):
            return jsonify({'status': 'lose', 'board': board})
        if is_board_full(board):
            return jsonify({'status': 'draw', 'board': board})

    return jsonify({'status': 'continue', 'board': board})


@app.route('/restart', methods=['POST'])
def restart_game():
    global board
    board = [None] * 9
    return jsonify({'board': board})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
