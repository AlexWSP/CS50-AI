"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    numX = 0
    numO = 0
    
    for row in board:
        numX += row.count(X)
        numO += row.count(O)

    if numX <= numO:
        return X
    else:
        return O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    possible_actions = set()
    
    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                possible_actions.add((i, j))

    return possible_actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    if action not in actions(board):
        raise Exception("Invalid move")

    copy_board = copy.deepcopy(board)
    (i, j) = action
    copy_board[i][j] = player(board)

    return copy_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # check horizontal
    for row in range(3):
        if all(board[row][col] == X for col in range(3)):
            return X
        if all(board[row][col] == O for col in range(3)):
            return O

    # check vertical
    for col in range(3):
        if all(board[row][col] == X for row in range(3)):
            return X
        if all(board[row][col] == O for row in range(3)):
            return O

    # check diagonal
    diagonal = [[(0, 0), (1, 1), (2, 2)], [(0, 2), (1, 1), (2, 0)]]
    for diag in diagonal:
        if all(board[row][col] == X for (row, col) in diag):
            return X
        if all(board[row][col] == O for (row, col) in diag):
            return O

    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) != None:
        return True

    for row in board:
        for cell in row:
            if cell == EMPTY:
                return False

    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if winner(board) == X:
        return 1
    elif winner(board) == O:
        return -1
    else:
        return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None

    if player(board) == X:
        optimal_v = -math.inf
        for action in actions(board):
            max_v = MIN_v(result(board, action))
            if max_v > optimal_v:
                optimal_v = max_v
                optimal_action = action

    elif player(board) == O:
        optimal_v = math.inf
        for action in actions(board):
            min_v = MAX_v(result(board, action))
            if min_v < optimal_v:
                optimal_v = min_v
                optimal_action = action

    return optimal_action

def MIN_v(board):
    if terminal(board):
        return utility(board)

    v = math.inf
    for action in actions(board):
        v = min(v, MAX_v(result(board, action)))

    return v

def MAX_v(board):
    if terminal(board):
        return utility(board)

    v = -math.inf
    for action in actions(board):
        v = max(v, MIN_v(result(board, action)))

    return v
    
