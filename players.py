""" Implements the Player and AI classes """

from typing import Tuple
from random import randint
from board import Board
from time import time

class Player():
    """
    The Player class instantiates the player,
    lets them make a move, and updates their score
    """

    PlayerNumber = 0

    def __init__(self):
        """ Initialize a player """
        self.moves = [] # stack for undos
        self.score = 0 # number of games won
        self.mark = 'O' if Player.PlayerNumber == 0 else 'X'
        self.player_num = Player.PlayerNumber
        Player.PlayerNumber += 1

    def get_move(self, board:Board) -> Tuple[int, int]:
        """ For the base player, the human player makes a move with mouse """
        # get mouse click
        while True:
            clickPoint = board.window.getMouse()
            tile_x = int(clickPoint.getX() // board.tile_size)
            tile_y = int(clickPoint.getY() // board.tile_size)
            move = (tile_x, tile_y, self.mark)

            if board.check_legal(move):
                break

        return move 

class AI(Player):
    
    def __init__(self, depth:int, branch_factor:int) -> None:
        """ Initialize the AI player """
        super().__init__()
        self.minimax_depth = depth
        self.branch_factor = branch_factor
        self.transposition_table = dict()

    def get_possible_moves(self, board:Board, maximizer:bool) -> Tuple[list, list]:
        """ Get the possible moves AI can take on a given board position """        

        mark = 'O' if maximizer else 'X'
        possible_moves = []
        x_fav = []
        o_fav = []
        both_fav = []

        for tile_y in range(len(board.tiles)):
            for tile_x in range(len(board.tiles[tile_y])):
                if board.check_legal((tile_x, tile_y, mark)):
                    score_X = board.logic[tile_y][tile_x].get_value_mark('X')
                    score_O = board.logic[tile_y][tile_x].get_value_mark('O') 
                    if score_X != 0 or score_O != 0:
                        if -score_X > score_O:
                            x_fav.append(((score_X, score_O), (tile_x, tile_y, mark)))
                        else:
                            o_fav.append(((score_X, score_O), (tile_x, tile_y, mark)))

        x_fav = [move for move in sorted(x_fav, key=lambda x: x[0][0])]
        o_fav = [move for move in sorted(o_fav, key=lambda o: o[0][1])]

        return (x_fav, o_fav)

    def update_possible_moves(self, curr_poss: list, changed: list, move: tuple, board: Board) -> list:
        """
        Update possible moves for player to try.
        :param changed: constant 16 tiles whose values were changed
        :curr_pos: constant branch_factor number of moves
        """
        new_poss_moves = []
        poss_x, poss_o = curr_poss
        move_x, move_o = move[0], move[1]
        nxt_mark = 'X' if move[2] == 'O' else 'O'

        x_fav = []
        o_fav = []
        to_remove = {(move_x, move_o): 1}

        for (tile_x, tile_y), _ in changed:
            tile = board.logic[tile_y][tile_x]
            to_remove[(tile_x, tile_y)] = 1

            score_X = tile.get_value_mark('X')
            score_O = tile.get_value_mark('O') 

            if score_X != 0 or score_O != 0:
                if -score_X > score_O:
                    x_fav.append(((score_X, score_O), (tile_x, tile_y, nxt_mark)))
                else:
                    o_fav.append(((score_X, score_O), (tile_x, tile_y, nxt_mark)))
            
            # new_poss_moves.append(((-sum(tile.len_chains_X), sum(tile.len_chains_O)), (tile_x, tile_y, nxt_mark)))
        
        poss_x = [poss for poss in poss_x if (poss[1][0], poss[1][1]) not in to_remove]
        poss_o = [poss for poss in poss_o if (poss[1][0], poss[1][1]) not in to_remove]

        # breakpoint()
        x_fav = [(poss[0], (poss[1][0], poss[1][1], nxt_mark)) for poss in sorted(poss_x + x_fav, key=lambda x: x[0][0])]
        o_fav = [(poss[0], (poss[1][0], poss[1][1], nxt_mark)) for poss in sorted(poss_o + o_fav, key=lambda o: o[0][1])]
        
        return (x_fav, o_fav)
                
    def get_move(self, board:Board, depth:int=5, branch_factor:int=20) -> tuple:
        """ Let the AI make a move given a board configuration """
        maximizer = self.mark == 'O'
        poss_x, poss_o = self.get_possible_moves(board, maximizer)
        self.hash_queries_success = 0
        self.num_states_searched = 0

        (move, _), _ = self.negamaxAB(board, maximizer, depth, branch_factor, poss_moves=(poss_x, poss_o))
        print(f"Searched {self.num_states_searched} states, of which {self.hash_queries_success} are retrieved from the transposition table")

        return move
    
    def get_move_iterative_deepening(self, board: Board, depth: int=5, branch_factor: int=20, time_lim: float=5) -> tuple:
        
        maximizer = self.mark == 'O'
        max_depth = depth
        cur_depth = 1

        poss_x, poss_o = self.get_possible_moves(board, maximizer)

        self.hash_queries_success = 0
        self.num_states_searched = 0

        start = time()
        while time() - start < time_lim and cur_depth <= max_depth:
            (move, _), choices = self.negamaxAB(board, maximizer, cur_depth, branch_factor, poss_moves=(poss_x, poss_o), move_is_ordered=cur_depth != 1)

            cur_depth += 1
            # reorder possible moves for better pruning
            choice_dict = {move: state_score * (1 if maximizer else -1) for move, state_score in choices}
            poss = sorted(poss_x + poss_o, key=lambda poss: choice_dict[poss[1]] if poss[1] in choice_dict else 0)
            poss_x, poss_o = poss[:len(poss) // 2], poss[len(poss)//2:]

        print(f"Searched {self.num_states_searched} states, of which {self.hash_queries_success} are retrieved from the transposition table")

        return move
    
    def negamaxAB(self, board:Board, maximizer:bool, depth:int=5, branch_factor:int=10, \
                poss_moves:tuple=(None, None), alpha=float('-inf'), beta=float('inf'), \
                move_is_ordered: bool=False) -> Tuple[float, tuple]: 

        """ Return the score the player can achieve at that state with curr_depth
        :param board: the current board
        :param alpha: the worst the maximizer can do
        :param beta: the worst the minimizer can do
        :param maximizer: whether the player want to maximize or minimize the board's score
        :param depth: the maximum depth the player can see ahead
        :param branch_factor: the number of moves the player can consider at any given depth
        :param poss_moves: the moves the player will choose and search from
        :param move_is_ordered: whether the given poss_moves is already ordered or not
        :return: the score the player think they can achieve.
        """
        if move_is_ordered is False:
            poss_x, poss_o = poss_moves # determines branching factor

            if len(poss_x) + len(poss_o) >= branch_factor:
                if len(poss_x) < branch_factor // 2:
                    poss_o = poss_o[-(branch_factor - len(poss_x)):]
                elif len(poss_o) < branch_factor // 2:
                    poss_x = poss_x[:(branch_factor - len(poss_o))]
                else:
                    poss_x = poss_x[:(branch_factor // 2)]
                    poss_o = poss_o[-(branch_factor // 2):]

            # for a better move ordering
            if maximizer:
                poss = poss_o[::-1] + poss_x[::-1] 
            else:
                poss = poss_x + poss_o
        else:
            poss = poss_moves[0] + poss_moves[1]

        choices = []
        has_no_board = True
        
        for (score_x, score_y), move in poss:
            mark = move[2]
            nxt_mark = 'O' if mark == 'X' else 'X'

            self.num_states_searched += 1            
            orig_states = board.update_board(move, graphic=False)
            board_hash = board.get_bit_repr()

            try:
                state_score = self.transposition_table[(board_hash, depth)] * (1 if maximizer else -1)
                self.hash_queries_success += 1
            except KeyError:

                if board.check_win(move)[0]:
                    self.transposition_table[(board_hash, depth)] = float('inf') if maximizer else -float('inf')
                    board.undo_change(orig_states, move)
                    choices.append((move, float('inf')))
                    return (move, float('inf')), choices
                elif board.check_full():
                    self.transposition_table[(board_hash, depth)] = 0 
                    board.undo_change(orig_states, move)
                    choices.append((move, 0))
                    return (move, 0), choices

                if depth == 1:
                    state_score = Board.score_board(board) * (1 if maximizer else -1)
                else:
                    new_poss_moves = self.update_possible_moves(poss_moves, orig_states, move, board)

                    (_ , state_score), _ = \
                        self.negamaxAB(board, maximizer=(not maximizer), depth=depth-1, branch_factor=branch_factor, \
                                    poss_moves=new_poss_moves, alpha=-beta, beta=-alpha)
                    
                    state_score *= -1
                
            self.transposition_table[(board_hash, depth)] = state_score if maximizer else -state_score
            choices.append((move, state_score))
            board.undo_change(orig_states, move)

            if state_score > alpha:
                alpha = state_score
            if alpha > beta:
                break
        
        return max(choices, key=lambda x: x[1]), choices