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
        self.minimax_stack_depth = 0


    def get_possible_moves(self, board:Board, maximizer:bool, branch_factor:int) -> Tuple[list, list]:
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

        x_fav = [move for move in sorted(x_fav, key=lambda x: x[0][0])][:branch_factor//2]
        o_fav = [move for move in sorted(o_fav, key=lambda o: o[0][1])][-branch_factor//2:]
        # breakpoint()
        return (x_fav, o_fav) 

    def update_possible_moves(self, curr_poss: list, changed: list, move: tuple, \
                             board: Board, branch_factor: int, debug: bool=False) -> list:
        """
        Update possible moves for player to try.
        :param changed: constant 16 tiles whose values were changed
        :curr_pos: constant branch_factor number of moves
        """
        new_poss_moves = []
        poss_x, poss_o = curr_poss
        move_x, move_o = move[0], move[1]
        nxt_mark = 'X' if move[2] == 'O' else 'O'

        to_remove = {(move_x, move_o): 1}

        for (tile_x, tile_y), _ in changed:
            tile = board.logic[tile_y][tile_x]
            to_remove[(tile_x, tile_y)] = 1
            new_poss_moves.append(((-sum(tile.len_chains_X), sum(tile.len_chains_O)), (tile_x, tile_y, nxt_mark)))
        
        poss_x = [poss for poss in poss_x if (poss[1][0], poss[1][1]) not in to_remove]
        poss_o = [poss for poss in poss_o if (poss[1][0], poss[1][1]) not in to_remove]

        # breakpoint()

        x_fav = [poss for poss in new_poss_moves if poss[0][0] < 0]
        o_fav = [poss for poss in new_poss_moves if poss[0][1] > 0]

        x_fav = [(poss[0], (poss[1][0], poss[1][1], nxt_mark)) for poss in sorted(poss_x + x_fav, key=lambda x: x[0][0])]
        o_fav = [(poss[0], (poss[1][0], poss[1][1], nxt_mark)) for poss in sorted(poss_o + o_fav, key=lambda o: o[0][1])]

        new_poss_moves = (x_fav[:branch_factor//2], o_fav[-branch_factor//2:])
        return new_poss_moves
                
    def get_move(self, board:Board, depth:int=5, branch_factor:int=20) -> tuple:
        """ Let the AI make a move given a board configuration """
        # board.draw_logic_state()

        maximizer = self.mark == 'O'
        poss_x, poss_o = self.get_possible_moves(board, maximizer, branch_factor)

        move, _ = self.negamaxAB(board, maximizer, depth, branch_factor, poss_moves=(poss_x, poss_o))
        print(self.minimax_stack_depth)
        self.minimax_stack_depth = 0
        return move
    
    def iterative_deepening_search(self, board: Board, depth: int=5,\
                                branch_factor: int=10, time_limit: float =5):
        """
        Run iterative deepning search
        """
        # initialise some variables
        curr_maximizer = self.mark == 'O'
        curr_mark = self.mark
        nxt_mark = 'X' if curr_mark == 'O' else 'O'

        init_poss = self.get_possible_moves(board, curr_maximizer, branch_factor)
        init_state = []

        states = [init_state]
        poss_moves = [init_poss] # possible moves at the end of the sequence
        iter_depth = 1

        # default (and initial) best move
        if curr_maximizer:
            best_move = init_poss[1][-1] if len(init_poss[1]) > 0 else init_poss[0][0]
        else:
            best_move = init_poss[0][0] if len(init_poss[0]) > 0 else init_poss[1][-1]

        
        start = time()
        while time() - start <= time_limit and iter_depth <= depth:

            # at a certain depth, find state scores of possible states from that depth, before 
            # returning them upwards through minimax

            # for access at a later depth
            new_states = []
            new_poss_moves = []
            break_flag = False

            # each deeper level requires a rest of alpha-beta values
            alpha = float('-inf')
            beta = float('inf')

            # pass to calculate all state scores with alpha-beta pruning
            for i in range(len(states)):

                # get the state (sequence of moves leading to the board's state)
                # and the possible moves to be considered at the state
                state = states[i]
                poss_move = poss_moves[i]
                options = []

                # create a good move ordering
                if curr_maximizer:
                    poss = poss_move[1][:len(poss_move[1])//2] + poss_move[0][:len(poss_move[0])//2] + poss_move[1][len(poss_move[1])//2:] + poss_move[0][len(poss_move[0])//2:] 
                else:
                    poss = poss_move[0][:len(poss_move[0])//2] + poss_move[1][:len(poss_move[1])//2] + poss_move[0][len(poss_move[0])//2:] + poss_move[1][len(poss_move[1])//2:] 
                
                # breakpoint()
                board.update_state(state)

                # calculate the state_score by getting the min/max of all possible moves from the state
                for (score_x, score_o), move in poss:

                    changed = board.update_board(move, graphic=False)

                    # saves future states for further deepening
                    new_poss_moves.append(self.update_possible_moves(poss_move, changed, move, board, branch_factor))
                    new_states.append(state + [move])
                    board.undo_change(changed, move)
                    
                    if break_flag is False:
                        self.minimax_stack_depth += 1

                        if board.check_win(move)[0]:
                            state_score = float('inf') if move[2] == 'O' else -float('inf')
                        else:
                            state_score = Board.score_board(board)

                        # pruning
                        if curr_maximizer:
                            if state_score > beta:
                                break_flag = True
                        else:
                            if state_score < alpha:
                                break_flag = True

                        options.append((move, state_score))

                board.undo()
                
                if break_flag is False:
                    best, state_score = max(options, key=lambda x: x[1]) if curr_maximizer else min(options, key=lambda x: x[1])
                
                # going back from state score through minimax to find optimal move

                # breakpoint()
                if curr_maximizer:
                    alpha = state_score
                    if alpha < beta:
                        best_move = state[0]
                else:
                    if state_score < beta:
                        beta = state_score
                        if beta > alpha:
                            best_move = state[0]

                
            states = new_states
            poss_moves = new_poss_moves
            iter_depth += 1

            nxt_mark, curr_mark = curr_mark, nxt_mark
            curr_maximizer = not curr_maximizer

        # breakpoint()

        print("Searched {} moves.".format(self.minimax_stack_depth))

        return best_move
        

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

        # create a good move ordering
        # if maximizer:
        #     poss = poss_o[:len(poss_o)//2] + poss_x[:len(poss_x)//2] + poss_o[len(poss_o)//2:] + poss_x[len(poss_x)//2:] 
        # else:
        #     poss = poss_x[:len(poss_x)//2] + poss_o[:len(poss_o)//2] + poss_x[len(poss_x)//2:] + poss_o[len(poss_o)//2:] 
        
        if maximizer:
            poss = poss_o[::-1] + poss_x[::-1] 
        else:
            poss = poss_x + poss_o
        
        # poss = sorted(poss_x + poss_o, key=lambda poss: Board.score_move(board, poss[1]), reverse=maximizer)

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
                new_poss_moves = self.update_possible_moves(poss_moves, orig_states, move, board, branch_factor)
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