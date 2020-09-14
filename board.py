""" Implements the board class """

__author__ = 'Hoang Long Dang'

from graphics import Point, Circle, GraphWin, Line, Text
from copy import deepcopy
from typing import Tuple, TypeVar

T = TypeVar('T')
int_str = TypeVar('int_str', int, str)

class Tile():
    """
    Holds values for each tile in the board.
    Helper class for Board class
    """
    def __init__(self) -> None:
        self.len_chains_X = [0] * 8 # down, diagonal down, right, diagonal up, up, etc. anti-clockwise
        self.len_chains_O = [0] * 8

    def get_value_mark_place(self, j, mark):
        if mark == 'X':
            return self.len_chains_X[j]
        else:
            return self.len_chains_O[j]

    def get_value(self) -> int:
        """ return the value of a tile """
        return self.get_value_mark('O') + self.get_value_mark('X')

    def get_value_mark(self, mark:str) -> int:
        """ return the value of a tile with respect to one player only """
        if mark == 'X':
            return sum(self.len_chains_X) * -1
        else:
            return sum(self.len_chains_O) * 1

    def set_value(self, direct:int_str, mark:str, val:int) -> None:
        """ Set the value of the chain_length """
        if isinstance(direct, int):
            if mark == 'O': self.len_chains_O[direct] = val
            else: self.len_chains_X[direct] = val
        else:
            if mark == 'O': self.len_chains_O[directions[direct]] = val
            else: self.len_chains_X[directions[direct]] = val
        

class Board():
    """
    The Board class to instantiate the game, record player's moves,
    and return the internal logic state for AI players
    """

    ### UTILITY FUNCTIONS ### 
    def coord_tile_to_grid(self, tile_x:int, tile_y:int) -> Tuple[int, int]:
        """ Get the tile location and return pixel location """
        return (int((tile_x + 0.5) * self.tile_size), int((tile_y+0.5)*self.tile_size))

    def get_chains_mark(self, source:tuple, mark:str, extended:int=2) -> list:
        """ 
        From source, get consecutive chains of a certain mark until terminated by empty
        tiles or by a different mark. Return all empty tiles reachable this way and the length of the chain to it.
        :param source: (tile_x, tile_y)
        :param mark: 'X' or 'O'
        if extended == 0:
        :return: [ 8 (len_chain, (tile_x, tile_y)) tuples, except (0, None) if chain is terminated by tiles with opposite mark
        else:
        :return: [ 8 (len_chain, [(tile_x, tile_y) * extended]) tuples, except (0, []) if chain is terminated by tiles with opposite mark]
        """
        tile_x, tile_y = source
        in_grid = lambda x=None, y=None: (len(self.tiles[0]) > x >= 0) and (len(self.tiles) > y >= 0)
        directions = [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)] # down, diagonal down, right, diagonal up, ... anti clockwise
        cands = [0 for i in range(len(directions))]

        changed = [[] for i in range(len(directions))]

        for direct in range(8):
            i, (x, y), line_len, num_reached = 1, directions[direct], 0, 0
            while in_grid(x=tile_x+i*x, y=tile_y+i*y) and self.tiles[tile_y+i*y][tile_x+i*x] == mark:
                line_len += 1
                i += 1
            while num_reached < extended:
                if in_grid(x=tile_x+i*x, y=tile_y+i*y) and self.tiles[tile_y+i*y][tile_x+i*x] == 0: # this tile's value will be adjusted
                    changed[direct].append((tile_x+i*x, tile_y+i*y))
                    num_reached += 1
                    i += 1
                else:
                    break
            cands[direct] = line_len

        return [(cands[i], changed[i]) for i in range(8)]

    ### INSTANCE LOGIC METHODS ###

    def __init__(self, window_width:int, window_height:int, tile_size:int, win_length:int=5, verbose:bool=True) -> None:
        """ Initialize the game board with width, height, and tile-size """
        
        # Make sure tile size is even
        if verbose: print("Making sure tile size is even...")
        tile_size += tile_size % 2 == 1

        # Make sure window's sizes are divisible by tile size
        if verbose: print("Making sure grid can be evenly divided into equally sized tiles...")
        window_width = (window_width // tile_size) * tile_size
        window_height = (window_height // tile_size) * tile_size

        # Initialize...
        self.tiles = [[0] * len(range(tile_size // 2, window_width, tile_size)) for i in range(tile_size // 2, window_height, tile_size)]
        self.logic = [[Tile() for j in range(len(self.tiles[0]))] for i in self.tiles] # 4 values for 4 directions a chain can take

        self.window_width = window_width
        self.window_height = window_height
        self.tile_size = tile_size
        self.win_length = win_length
        self.window = None
        self.logic_window = None

    def check_win(self, move:tuple, win_length:int=5) -> Tuple[bool, Tuple[tuple, tuple]]:
        """ Check if a move wins the game 
        :param move: a valid move: (selected_tile.x_pos, selected_tile.y_pos, player.mark)
        :win_length: length of winning streak
        :return: a boolean value, a pair of tile-coordinates for the winning line (none if move doesn't win the game)
        """
        tile_x, tile_y, mark = move
        in_grid = lambda x=None, y=None: (len(self.tiles[0]) > x >= 0) and (len(self.tiles) > y >= 0)

        for x, y in [(1, 0), (0, 1), (1, -1), (1, 1)]: # For each pattern: vertical (only y change), horizontal (only x change), diagonal ...
            
            cand = []
            for i in range(-win_length+1, win_length):
                new_y = tile_y + i*y
                new_x = tile_x + i*x
                if in_grid(x=new_x,y=new_y) :
                    cand.append((self.tiles[new_y][new_x], (new_x, new_y)))

            # check if there are consecutives of mark of win_length in cand:
            if len(cand) >= win_length:
                for i in range(self.win_length):
                    seq = cand[i:i+self.win_length]
                    seq_mark = [x[0] for x in seq]
                    try:
                        seq_start = seq[0][1]
                        seq_end = seq[-1][1]
                    except:
                        breakpoint()
                    
                    if seq_mark == [mark] * self.win_length:
                        return True, (seq_start, seq_end)
        
        return False, None

    def check_legal(self, move:T) -> bool:
        """ Check whether a move is legal
        :param move: any value
        :return: True if move is legal, False otherwise
        """
        in_grid = lambda x, y: (len(self.tiles) > y >= 0) and (len(self.tiles[0]) > x >= 0)
        try:
            assert isinstance(move, tuple)
            assert len(move) == 3
            assert isinstance(move[-1], str)
            assert isinstance(move[0], int)
            assert isinstance(move[1], int)

            assert in_grid(move[0], move[1]) == True 
        except:
            return False

        return self.tiles[move[1]][move[0]] == 0

    def update_board(self, move:tuple, graphic:bool=True, logic:bool=True) -> list:
        """ Update the board based on a move. Can update graphically, logically, or either. 
        :param move: a legal move: (selected_tile.x_pos, selected_tile.y_pos, player.mark)
        :param graphic: if true (and there is a window), draw move
        :param logic: if true, update the board's logic state
        :return: List of update tiles and their original states (for the mark)
        """

        tile_x, tile_y, mark = move

        # update graphic
        if graphic and self.window:
            self.draw_mark(move)

        # update logic
        if logic:
            self.tiles[tile_y][tile_x] = mark
            nxt_mark = 'X' if mark == 'O' else 'O'
            
            same_chains = self.get_chains_mark((tile_x, tile_y), mark)
            same_changed = [x[1] for x in same_chains]

            diff_chains = self.get_chains_mark((tile_x, tile_y), nxt_mark)
            diff_changed = [x[1] if 4 > x[0] > 0 else [] for x in diff_chains]

            orig = []
            
            for i in range(8):
                j = i + 4 if i < 4 else i - 4

                same = len(same_changed[i]) != 0
                changed = same_changed[i] if same else diff_changed[i]
                if same:
                    len_chain = same_chains[i][0] + same_chains[j][0] + 1 
                    blocked = len(same_changed[j]) == 0

                for f in range(len(changed)):
                    (c_x, c_y) = changed[f]
                    tile = self.logic[c_y][c_x]
                    orig.append(((c_x, c_y), [deepcopy(tile.len_chains_O), deepcopy(tile.len_chains_X)]))

                    if same:
                        tile.set_value(j, mark, 1 + (len_chain - blocked)**2)

                    if tile.get_value_mark_place(i, nxt_mark)  > 0:
                        n = (tile.get_value_mark_place(i, nxt_mark) - 1) ** (1/2)
                        tile.set_value(i, nxt_mark, (n-1)**2 + 1)
                    if tile.get_value_mark_place(j, nxt_mark)  > 0:
                        n = (tile.get_value_mark_place(j, nxt_mark) - 1) ** (1/2)
                        tile.set_value(j, nxt_mark, (n-1)**2 + 1)

            return orig

        return [(None, None)]

    def undo_change(self, change:list, move:tuple) -> None:
        """ Undo the list of changes made by update_board """
        tile_x, tile_y, _ = move
        self.tiles[tile_y][tile_x] = 0
        
        for (tile_x, tile_y), [states_O, states_X] in change:
            self.logic[tile_y][tile_x].len_chains_O = states_O
            self.logic[tile_y][tile_x].len_chains_X = states_X

        return

    def update_state(self, state:list) -> None:
        """
        Update the board in a sequence of moves
        """
        self.state_changed = []

        for move in state:
            changed = self.update_board(move, graphic=False)
            self.state_changed.append((move, changed))

    def undo_state(self):
        """
        Undo a sequence of moves.
        The sequence of moves MUST have been applied through update_state function.
        """
        if self.state_changed:
            for move, changed in self.state_changed[::-1]:
                self.undo_change(changed, move)

    @staticmethod
    def score_board(board:'Board') -> float:
        """ Score the board value for the first player O. the higher the better """
        score = 0
        for y in range(len(board.logic)):
            for x in range(len(board.logic[0])):
                score += board.logic[y][x].get_value() 
        try:
            return float(score)
        except:
            breakpoint()

    @staticmethod
    def score_move(board: 'Board', move: tuple) -> float:
        """ Score the value of a move """
        changed = board.update_board(move, graphic=False)
        # res = Board.score_board(board)
        res = sum([board.logic[change[0][1]][change[0][0]].get_value() for change in changed])
        board.undo_change(changed, move)
        return res

    ### INSTANCE DRAW METHODS ###

    def draw_grid(self, logic:bool=False) -> None:
        """ Draw the board's grid """
        window = self.window if not logic else self.logic_window
        if window is not None:
            # draw horizontals:
            for i in range(self.tile_size, self.window_height, self.tile_size):
                row_y = i
                line = Line(Point(0,row_y), Point(self.window_width, row_y))
                line.setOutline('black')
                line.setWidth(2)
                line.draw(window)

            # draw verticals
            for i in range(self.tile_size, self.window_width, self.tile_size):
                col_x = i
                line = Line(Point(col_x, 0), Point(col_x, self.window_height))
                line.setOutline('black')
                line.setWidth(2)
                line.draw(window)

    def draw_mark(self, move:tuple) -> None:
        """ Draw a mark as specified by a move 
        :param move: a legal move: (selected_tile.x_pos, selected_tile.y_pos, player.mark)
        :return: none
        """

        if self.window is None:
            raise ValueError('Board has no open window!')

        tile_x, tile_y, mark = move
        
        grid_x, grid_y = self.coord_tile_to_grid(tile_x, tile_y)

        rad = self.tile_size * 0.3

        if mark == 'O':
            cir = Circle(Point(grid_x, grid_y), rad) 
            cir.setOutline('blue')
            cir.setWidth(3)
            cir.draw(self.window)
        else:
            downstroke = Line(Point(grid_x - rad, grid_y - rad), Point(grid_x + rad, grid_y + rad))
            upstroke = Line(Point(grid_x - rad, grid_y + rad), Point(grid_x + rad, grid_y - rad))
            downstroke.setOutline('red')
            downstroke.setWidth(3)
            upstroke.setOutline('red')
            upstroke.setWidth(3)
            upstroke.draw(self.window)
            downstroke.draw(self.window)
    
    def draw_winning_line(self, start:tuple, end:tuple) -> None:
        """ Draw a line through the winning series of marks """

        if self.window is None:
            raise ValueError("Board does not have an open window!")

        start_x, start_y = self.coord_tile_to_grid(start[0], start[1])
        end_x, end_y = self.coord_tile_to_grid(end[0], end[1])
        
        pt1 = Point(start_x, start_y)
        pt2 = Point(end_x, end_y)

        line = Line(pt1, pt2)
        line.setWidth(4)
        line.setOutline('black')
        line.draw(self.window)

    def draw_logic_state(self) -> None:
        """ Draw the logic state of the board """
        self.logic_window = GraphWin("Logic states", self.window_width, self.window_height)
        self.draw_grid(logic=True)
        for y in range(len(self.tiles)):
            for x in range(len(self.tiles[0])):
                grid_x, grid_y = self.coord_tile_to_grid(x, y)

                # tile_val_txt = Text(Point(grid_x, grid_y), "{:.1f}".format(sum(self.logic[y][x])))
                tile_val_txt = Text(Point(grid_x, grid_y), "{}, {}".format(int(sum(self.logic[y][x].len_chains_O)), -int(sum(self.logic[y][x].len_chains_X))))
                tile_val_txt.setSize(15)
                tile_val_txt.setFace('courier')
                tile_val_txt.draw(self.logic_window)

                if isinstance(self.tiles[y][x], str):
                    color = 'red' if self.tiles[y][x] == 'X' else 'blue'
                    tile_val_txt.setTextColor(color)


        self.logic_window.getMouse()
        self.logic_window.close()