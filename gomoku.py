from board import Board
from players import Player, AI
from graphics import GraphWin

from time import time

# TODO
# implement iterative deepening for better move ordering
# implement hashtable
# implement quiescent search
# optimize some helper methods
# create buttons and other GUI elements
# create undo features


def main():
    """ run the game """
    # Board init
    window_width, window_height, tile_size = [int(i.strip("")) for i in input("Enter window width, height, and tile size:\n").split(" ")]
    board = Board(window_width, window_height, tile_size)

    # Players init
    player1 = Player()
    play_AI = input("Do you want to player with AI? [y/n]: ")
    if play_AI == 'y':
        minimax_depth = int(input("\nEnter AI player maximum depth for minimax: "))
        branch_factor = int(input("Enter AI player branch factor: "))
        player2 = AI(minimax_depth, branch_factor)
    else:
        player2 = Player()

    # Run game
    board.window = GraphWin('Tic Tac Toe', board.window_height, board.window_width)
    board.draw_grid()
    print("Begin Game!")
    
    turn = 0
    win = False
    while not win:
        if turn % 2 == 0:
            move = player1.get_move(board)
        else:
            if play_AI == 'y':
                start = time()
                # move = player2.get_move(board, depth=player2.minimax_depth, branch_factor=player2.branch_factor)
                move = player2.get_move_iterative_deepening(board, player2.minimax_depth, player2.branch_factor, 5)
                end = time()
                print("Time elapsed for move {} is {:2f}s".format(turn + 1, end - start))
            else:
                move = player2.get_move(board)
        changed = board.update_board(move)
        win, pos = board.check_win(move)
        
        if turn == 6:
            breakpoint()

        if win:
            board.draw_winning_line(pos[0], pos[1])
            break

        if not board.check_full():
            turn += 1
        else:
            break

    if board.check_full() is False:
        print("Player {} wins!".format(2 - int(turn % 2 == 0)))
    else:
        print("The game is a tie!")

    board.window.getMouse()
    board.window.close()


if __name__ == '__main__':
    main()