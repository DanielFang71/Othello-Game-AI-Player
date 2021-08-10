"""
An AI player for Othello.
"""
# For my own heuristic, I use four values: utility, stable, move and weight.
# The utility value is the difference between each player's pieces count.
# The stable value is the count of stable pieces which is on the corners or edges,
# also I add a check for the pieces which can form a line with corner pieces with
# same color, in this case, they are stable,too.
# For the move, it is the the count difference between us and opponent.
# For weight, the utility value is weight heavy and a little increase at final stage
# since it is a good measure of heuristic for the whole game and in the final stage
# can be a good mesure of win.
# And for stable, I use the most heavy weight since If play control the corners or
# edges they can have more pieces secured.
# For move, rif we can reduce opponent's move count at the opening stage,
# it would indicate a good heuristic. And as game move on, there are limited amount of
# difference for possible moving count, so the weight is decreasing.

import sys

# You can use the functions in othello_shared to write your AI
from othello_shared import get_possible_moves, get_score, play_move

# Global dictionary for states caching
# Key is a tuple (board,color) and value is its minimax value
# The color is the one which results in this board
state_dict = {}


def eprint(*args,
           **kwargs):
    # you can use this for debugging, as it will print to sterr and not stdout
    print(*args, file=sys.stderr, **kwargs)


# Method to compute utility value of terminal state
def compute_utility(board, color):
    p1_count, p2_count = get_score(board)
    if color == 1:
        return p1_count - p2_count
    else:
        return p2_count - p1_count
    # change this!


# Better heuristic value of board
def compute_heuristic(board, color):
    # IMPLEMENT
    value = compute_utility(board, color)
    stable_val = compute_stable(board, color)
    moves_val = compute_move(board, color)
    stage = compute_stage(board)
    heur_val = value * stage[0] + stable_val * stage[1] + moves_val * stage[2]
    if get_possible_moves(board, color) == 0 \
            or get_possible_moves(board,opponent(color)) == 0:
        return value
    return heur_val


def compute_stable(board, color):
    size = len(board)
    stable_val = 0
    # corners
    if board[0][0] == color:
        stable_val += 50
    if board[0][-1] == color:
        stable_val += 50
    if board[-1][0] == color:
        stable_val += 50
    if board[-1][-1] == color:
        stable_val += 50
    # edges
    stable_val += board[0].count(color) * 5
    stable_val += board[-1].count(color) * 5
    for i in range(size):
        count_1 = 1 if board[i][0] == color else 0
        count_2 = 1 if board[i][-1] == color else 0
        stable_val += (count_1 + count_2) * 5
    # stable cases as they cannot be flipped when they are connected to the corner and form a line
    if board[0][0] == color:
        i = 1
        j = 1
        while i < size and board[i][0] == color:
            stable_val += 5
            i += 1
        while j < size and board[0][j] == color:
            stable_val += 5
            j += 1
    if board[0][-1] == color:
        i = 1
        j = size - 2
        while i < size and board[i][-1] == color:
            stable_val += 5
            i += 1
        while j >= 0 and board[0][j] == color:
            stable_val += 5
            j -= 1
    if board[-1][0] == color:
        i = size - 2
        j = 1
        while i >= 0 and board[i][0] == color:
            stable_val += 5
            i -= 1
        while j < size and board[-1][j] == color:
            stable_val += 5
            j += 1
    if board[-1][-1] == color:
        i = size - 2
        j = size - 2
        while i >= 0 and board[i][-1] == color:
            stable_val += 5
            i -= 1
        while j >= 0 and board[-1][j] == color:
            stable_val += 5
            j -= 1
    return stable_val


def compute_move(board, color):
    dark = len(get_possible_moves(board, 1))
    light = len(get_possible_moves(board, 2))
    if color == 1:
        return dark - light
    else:
        return light - dark


def compute_stage(board):
    total = len(board) * len(board)
    p1, p2 = get_score(board)
    take = p1 + p2
    ratio = take / total
    weight_1 = (10, 1000, 10)
    weight_2 = (10, 1000, 5)
    weight_3 = (50, 1000, 1)
    if ratio <= 1 / 3:
        return weight_1
    elif 1 / 3 < ratio <= 2 / 3:
        return weight_2
    else:
        return weight_3


def save_cache(board, move, color, value, caching):
    """
    A helper function to save board and minimax value to cache dictionary.
    This function will write to dictionary iff caching is on (i.e. 1)
    and board is not in the dictionary.
    Last variable is to indicate the dictionary to store
    """
    if caching:
        state_dict[(board, color)] = (move, value)


def opponent(color):
    """
    A helper to return the opponent color
    """
    result = 2 if color == 1 else 1
    return result


############ MINIMAX ###############################
def minimax_min_node(board, color, limit, caching=0):
    if caching and (board, color) in state_dict:
        return state_dict[(board, color)]
    best_move = (0, 0)
    value = float('INF')
    possible_moves = get_possible_moves(board, opponent(color))
    if possible_moves == [] or limit == 0:
        result_utility = compute_utility(board, color)
        save_cache(board, best_move, color, result_utility, caching)
        return best_move, result_utility
    for move in possible_moves:
        nxt_board = play_move(board, opponent(color), move[0], move[1])
        nxt_move, nxt_val = minimax_max_node(nxt_board, color, limit - 1,
                                             caching)
        if value > nxt_val:
            value = nxt_val
            best_move = move
    save_cache(board, best_move, color, value, caching)
    return best_move, value


def minimax_max_node(board, color, limit,
                     caching=0):  # returns highest possible utility
    if caching and (board, color) in state_dict:
        return state_dict[(board, color)]
    best_move = (0, 0)
    value = float('-INF')
    possible_moves = get_possible_moves(board, color)
    if possible_moves == [] or limit == 0:
        result_utility = compute_utility(board, color)
        save_cache(board, best_move, color, result_utility, caching)
        return best_move, result_utility
    for move in possible_moves:
        nxt_board = play_move(board, color, move[0], move[1])
        nxt_move, nxt_val = minimax_min_node(nxt_board, color, limit - 1,
                                             caching)
        if value < nxt_val:
            value, best_move = nxt_val, move
    save_cache(board, best_move, color, value, caching)
    return best_move, value


def select_move_minimax(board, color, limit, caching=0):
    """
    Given a board and a player color, decide on a move.
    The return value is a tuple of integers (i,j), where
    i is the column and j is the row on the board.

    Note that other parameters are accepted by this function:
    If limit is a positive integer, your code should enfoce a depth limit that is equal to the value of the parameter.
    Search only to nodes at a depth-limit equal to the limit.  If nodes at this level are non-terminal return a heuristic
    value (see compute_utility)
    If caching is ON (i.e. 1), use state caching to reduce the number of state evaluations.
    If caching is OFF (i.e. 0), do NOT use state caching to reduce the number of state evaluations.
    """
    return minimax_max_node(board, color, limit, caching)[0]  # change this!


############ ALPHA-BETA PRUNING #####################
def alphabeta_min_node(board, color, alpha, beta, limit, caching=0, ordering=0):
    if caching and (board, color) in state_dict:
        return state_dict[(board, color)]
    best_move = (0, 0)
    value = float('INF')
    possible_moves = get_possible_moves(board, opponent(color))
    if possible_moves == [] or limit == 0:
        result_utility = compute_utility(board, color)
        save_cache(board, best_move, color, result_utility, caching)
        return best_move, result_utility
    board_map = {}
    for move in possible_moves:
        nxt_board = play_move(board, opponent(color), move[0], move[1])
        board_map[move] = nxt_board
    if ordering:
        board_map = dict(sorted(board_map.items(),
                                key=lambda item: compute_utility(item[1],
                                                                 color)))
    for move, new_board in board_map.items():
        nxt_move, nxt_val = alphabeta_max_node(new_board, color, alpha, beta,
                                               limit - 1, caching, ordering)
        if value > nxt_val:
            value, best_move = nxt_val, move
        if alpha >= value:
            break
        beta = min(value, beta)
    save_cache(board, best_move, color, value, caching)
    return best_move, value


def alphabeta_max_node(board, color, alpha, beta, limit, caching=0, ordering=0):
    if caching and (board, color) in state_dict:
        return state_dict[(board, color)]
    best_move = (0, 0)
    value = float('-INF')
    possible_moves = get_possible_moves(board, color)
    if not possible_moves or limit == 0:
        result_utility = compute_utility(board, color)
        save_cache(board, best_move, color, result_utility, caching)
        return best_move, result_utility
    board_map = {}
    for move in possible_moves:
        nxt_board = play_move(board, color, move[0], move[1])
        board_map[move] = nxt_board
    if ordering:
        board_map = dict(sorted(board_map.items(),
                                key=lambda item: compute_utility(item[1],
                                                                 color),
                                reverse=True))
    for move, new_board in board_map.items():
        nxt_move, nxt_val = alphabeta_min_node(new_board, color, alpha, beta,
                                               limit - 1, caching, ordering)
        if nxt_val > value:
            value, best_move = nxt_val, move
        if value >= beta:
            break
        alpha = max(value, alpha)
    save_cache(board, best_move, color, value, caching)
    return best_move, value  # change this!


def select_move_alphabeta(board, color, limit, caching=0, ordering=0):
    """
    Given a board and a player color, decide on a move.
    The return value is a tuple of integers (i,j), where
    i is the column and j is the row on the board.

    Note that other parameters are accepted by this function:
    If limit is a positive integer, your code should enfoce a depth limit that is equal to the value of the parameter.
    Search only to nodes at a depth-limit equal to the limit.  If nodes at this level are non-terminal return a heuristic
    value (see compute_utility)
    If caching is ON (i.e. 1), use state caching to reduce the number of state evaluations.
    If caching is OFF (i.e. 0), do NOT use state caching to reduce the number of state evaluations.
    If ordering is ON (i.e. 1), use node ordering to expedite pruning and reduce the number of state evaluations.
    If ordering is OFF (i.e. 0), do NOT use node ordering to expedite pruning and reduce the number of state evaluations.
    """
    return alphabeta_max_node(board, color, float("-Inf"), float("Inf"), limit,
                              caching, ordering)[0]  # change this!


####################################################
def run_ai():
    """
    This function establishes communication with the game manager.
    It first introduces itself and receives its color.
    Then it repeatedly receives the current score and current board state
    until the game is over.
    """
    print("Othello AI")  # First line is the name of this AI
    arguments = input().split(",")

    color = int(
        arguments[0])  # Player color: 1 for dark (goes first), 2 for light.
    limit = int(arguments[1])  # Depth limit
    minimax = int(arguments[2])  # Minimax or alpha beta
    caching = int(arguments[3])  # Caching
    ordering = int(arguments[4])  # Node-ordering (for alpha-beta only)

    if (minimax == 1):
        eprint("Running MINIMAX")
    else:
        eprint("Running ALPHA-BETA")

    if (caching == 1):
        eprint("State Caching is ON")
    else:
        eprint("State Caching is OFF")

    if (ordering == 1):
        eprint("Node Ordering is ON")
    else:
        eprint("Node Ordering is OFF")

    if (limit == -1):
        eprint("Depth Limit is OFF")
    else:
        eprint("Depth Limit is ", limit)

    if (minimax == 1 and ordering == 1):
        eprint("Node Ordering should have no impact on Minimax")

    while True:  # This is the main loop
        # Read in the current game status, for example:
        # "SCORE 2 2" or "FINAL 33 31" if the game is over.
        # The first number is the score for player 1 (dark), the second for player 2 (light)
        next_input = input()
        status, dark_score_s, light_score_s = next_input.strip().split()
        dark_score = int(dark_score_s)
        light_score = int(light_score_s)

        if status == "FINAL":  # Game is over.
            print
        else:
            board = eval(input())  # Read in the input and turn it into a Python
            # object. The format is a list of rows. The
            # squares in each row are represented by
            # 0 : empty square
            # 1 : dark disk (player 1)
            # 2 : light disk (player 2)

            # Select the move and send it to the manager
            if (minimax == 1):  # run this if the minimax flag is given
                movei, movej = select_move_minimax(board, color, limit, caching)
            else:  # else run alphabeta
                movei, movej = select_move_alphabeta(board, color, limit,
                                                     caching, ordering)

            print("{} {}".format(movei, movej))


if __name__ == "__main__":
    run_ai()
