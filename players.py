""" Implements the Player and AI classes """

from typing import Tuple
from random import randint
from board import Board

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
        self.minimax_stack_depth = 0

    def get_possible_moves(self, board:Board, maximizer:bool) -> Tuple[list, list]:
        """ Get the possible moves AI can take on a given board position """        

        mark = 'O' if maximizer else 'X'
        possible_moves = []

        for tile_y in range(len(board.tiles)):
            for tile_x in range(len(board.tiles[tile_y])):
                if board.check_legal((tile_x, tile_y, mark)):
                    score_X = board.logic[tile_y][tile_x].get_value_mark('X')
                    score_O = board.logic[tile_y][tile_x].get_value_mark('O') 
                    if score_X != 0 or score_O != 0:
                        possible_moves.append(((score_X, score_O), (tile_x, tile_y, mark)))

        x_fav = [move for move in possible_moves if move[0][0] < 0]
        o_fav = [move for move in possible_moves if move[0][1] > 0]

        x_fav = [move for move in sorted(x_fav, key=lambda x: x[0][0])]
        o_fav = [move for move in sorted(o_fav, key=lambda o: o[0][1])]
        # breakpoint()
        return (x_fav, o_fav) 

    def update_possible_moves(self, curr_poss, changed, nxt_mark, move, board) -> list:
        """
        Update possible moves for player to try.
        :param changed: constant 16 tiles whose values were changed
        :curr_pos: constant branch_factor number of moves
        """
        new_poss_moves = []
        to_remove = dict()
        poss_x, poss_o = curr_poss

        for (tile_x, tile_y), _ in changed:
            tile = board.logic[tile_y][tile_x]
            to_remove[(tile_x, tile_y)] = 1
            new_poss_moves.append(((-sum(tile.len_chains_X), sum(tile.len_chains_O)), (tile_x, tile_y, nxt_mark)))
        
        poss_x = [poss for poss in poss_x if (poss[1][0], poss[1][1]) not in to_remove]
        poss_o = [poss for poss in poss_o if (poss[1][0], poss[1][1]) not in to_remove]

        x_fav = [poss for poss in new_poss_moves if poss[0][0] < 0]
        o_fav = [poss for poss in new_poss_moves if poss[0][1] > 0]

        x_fav = [(poss[0], (poss[1][0], poss[1][1], nxt_mark)) for poss in sorted(poss_x + x_fav, key=lambda x: x[0][0]) if poss[1] != move]
        o_fav = [(poss[0], (poss[1][0], poss[1][1], nxt_mark)) for poss in sorted(poss_o + o_fav, key=lambda o: o[0][1]) if poss[1] != move]

        new_poss_moves = (x_fav, o_fav)
        return new_poss_moves
                
    def get_move(self, board:Board, depth:int=5, branch_factor:int=20) -> tuple:
        """ Let the AI make a move given a board configuration """
        # board.draw_logic_state()

        maximizer = self.mark == 'O'
        poss_x, poss_o = self.get_possible_moves(board, maximizer)
        poss_x = poss_x[:branch_factor//2]
        poss_o = poss_o[-branch_factor//2:]

        move, _ = self.negamaxAB(board, maximizer, depth, branch_factor, poss_moves=(poss_x, poss_o))
        print(self.minimax_stack_depth)
        self.minimax_stack_depth = 0
        return move

    def negamaxAB(self, board:Board, maximizer:bool, depth:int=5, branch_factor:int=10, \
                poss_moves:tuple=(None, None), alpha=float('-inf'), beta=float('inf')) -> Tuple[float, tuple]: 
        """ Return the score the player can achieve at that state with curr_depth
        :param board: the current board
        :param alpha: the worst the maximizer can do
        :param beta: the worst the minimizer can do
        :param maximizer: whether the player want to maximize or minimize the board's score
        :param depth: the maximum depth the player can see ahead
        :return: the score the player think they can achieve.
        """
        poss_x, poss_o = poss_moves # determines branching factor
        poss_x = poss_x[:branch_factor//2]
        poss_o = poss_o[-branch_factor//2:][::-1]

        # create a good move ordering
        if maximizer:
            poss = poss_o[:len(poss_o)//2] + poss_x[:len(poss_x)//2] + poss_o[len(poss_o)//2:] + poss_x[len(poss_x)//2:] 
        else:
            poss = poss_x[:len(poss_x)//2] + poss_o[:len(poss_o)//2] + poss_x[len(poss_x)//2:] + poss_o[len(poss_o)//2:] 

        # board.draw_logic_state()
        choices = []

        for (score_x, score_y), move in poss:
            mark = move[2]
            nxt_mark = 'O' if mark == 'X' else 'X'

            self.minimax_stack_depth += 1
            
            orig_states = board.update_board(move, graphic=False)
            if board.check_win(move)[0]:
                board.undo_change(orig_states, move)
                return (move, float('inf'))
            if depth == 1:
                nxt_ply_score = Board.score_board(board) * (1 if maximizer else -1)
            else:
                new_poss_moves = self.update_possible_moves(poss_moves, orig_states, nxt_mark, move, board)
                nxt_move , nxt_ply_score = \
                    self.negamaxAB(board, maximizer=(not maximizer), depth=depth-1, branch_factor=branch_factor, \
                                 poss_moves=new_poss_moves, alpha=-beta, beta=-alpha)
                nxt_ply_score *= -1

            choices.append((move, nxt_ply_score))
            board.undo_change(orig_states, move)

            if nxt_ply_score > alpha:
                alpha = nxt_ply_score
            if alpha > beta:
                break
                
        return max(choices, key=lambda x: x[1])