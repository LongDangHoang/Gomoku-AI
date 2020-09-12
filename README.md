# This is a simple attempt at a Gomoku (m-n-k) game AI, using minimax algorithm.
While some optimizations are added, this project is simply for personal practice with python and recursive algorithm. The AI is not very smart, and with about 10s of thinking it can play pretty well, but nowhere near expert level.

## Playing
Run the game by running the file gomoku.py using the python interpreter in the command line:

``` bash
python3 gomoku.py
```

Enter values as prompted:
* Board's width and height: in pixels. These values are for the game's window and are permanent (the window cannot be resized).
* Tile's size: in pixels. Length of a tile's edge. A tile is always square and always fill up evenly within the window. Thus, the tile's size must be a common divisor of the board's width and height. If not, adjustments are automatically made.
* Play with AI: y for yes, any other character for no.
* Minimax-depth: number of moves the AI will look ahead. 4-5 is recommended.
* Branch-factor: number of moves the AI consider at any depth level. 10 is recommended.

Click the board once a player wins to close the game.

## Issues
* The AI is very slow. It processes about 2000 game states a second, but at depth 7 it has to process around 60000 game states anyway.
* The AI is not very smart. While aggressive, it does not plan ahead for more tactical and complicated plays.
* This is probably due to both the game's representation as arrays and complicated tiles with evaluation functions, and Python's slowness when it comes to these massive search.
* The algorithms have not yet been polished. Possible additions include negascout, transposition table (experimented with before being removed with a large git reset alongside various ad-hoc optimisations that don't work), iterative deepening, and dynamic depth adjustment (ignore static game states to spend more time on game states with stronger potential)
