from dlgo.goboard import Move


def is_ladder_capture(game_state, candidate, recursion_depth=50):
    return is_ladder(True, game_state, candidate, None, recursion_depth)


def is_ladder_escape(game_state, candidate, recursion_depth=50):
    return is_ladder(False, game_state, candidate, None, recursion_depth)


def is_ladder(try_capture, game_state, candidate,
              ladder_stones=None, recursion_depth=50):
    """Ladders are played out in reversed roles, one player tries to capture,
    the other to escape. We determine the ladder status by recursively calling
    is_ladder in opposite roles, providing suitable capture or escape candidates.

    Arguments:
    try_capture: boolean flag to indicate if you want to capture or escape the ladder
    game_state: current game state, instance of GameState
    candidate: a move that potentially leads to escaping the ladder or capturing it, instance of Move
    ladder_stones: the stones to escape or capture, list of Point. Will be inferred if not provided.
    recursion_depth: when to stop recursively calling this function, integer valued.

    Returns True if game state is a ladder and try_capture is true (the ladder captures)
    or if game state is not a ladder and try_capture is false (you can successfully escape)
    and False otherwise.
    """

    if not game_state.is_valid_move(Move(candidate)) or not recursion_depth:
        return False

    next_player = game_state.next_player
    capture_player = next_player if try_capture else next_player.other
    escape_player = capture_player.other

    if ladder_stones is None:
        ladder_stones = guess_ladder_stones(game_state, candidate, escape_player)

    for ladder_stone in ladder_stones:
        current_state = game_state.apply_move(candidate)

        if try_capture:
            candidates = determine_escape_candidates(
                game_state, ladder_stone, capture_player)
            attempted_escapes = [  # now try to escape
                is_ladder(False, current_state, escape_candidate,
                          ladder_stone, recursion_depth - 1)
                for escape_candidate in candidates]

            if not any(attempted_escapes):
                return True  # if at least one escape fails, we capture
        else:
            if count_liberties(current_state, ladder_stone) >= 3:
                return True  # successful escape
            if count_liberties(current_state, ladder_stone) == 1:
                continue  # failed escape, others might still do
            candidates = liberties(current_state, ladder_stone)
            attempted_captures = [  # now try to capture
                is_ladder(True, current_state, capture_candidate,
                          ladder_stone, recursion_depth - 1)
                for capture_candidate in candidates]
            if any(attempted_captures):
                continue  # failed escape, try others
            return True  # candidate can't be caught in a ladder, escape.
    return False  # no captures / no escapes


def is_candidate(game_state, move, player):
    return game_state.next_player == player and \
        count_liberties(game_state, move) == 2


def guess_ladder_stones(game_state, move, escape_player):
    adjacent_strings = [game_state.board.get_go_string(nb) for nb in move.neighbors() if game_state.board.get_go_string(nb)]
    if adjacent_strings:
        string = adjacent_strings[0]
        neighbors = []
        for string in adjacent_strings:
            stones = string.stones
            for stone in stones:
                neighbors.append(stone)
        return [Move(nb) for nb in neighbors if is_candidate(game_state, Move(nb), escape_player)]
    else:
        return []


def determine_escape_candidates(game_state, move, capture_player):
    escape_candidates = move.neighbors()
    for other_ladder_stone in game_state.board.get_go_string(move).stones:
        for neighbor in other_ladder_stone.neighbors():
            right_color = game_state.color(neighbor) == capture_player
            one_liberty = count_liberties(game_state, neighbor) == 1
            if right_color and one_liberty:
                escape_candidates.append(liberties(game_state, neighbor))
    return escape_candidates


def count_liberties(game_state, move):
    if game_state.board.get_go_string(move):
        return game_state.board.get_go_string(move).num_liberties
    else:
        return 0


def liberties(game_state, move):
    return list(game_state.board.get_go_string(move).liberties)
