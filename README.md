# janissary

## To install with development requirements

`pip install -e .[dev]`

## Project Structure

The parsing of log files is broken up into sections: the header and the body. 
The header is written at the start of game, and contains information about the 
game settings, players, and initial conditions. The body contains a log of all
actions taken by players. Note that there is no state information stored in 
the log file, only the actions taken by players (e.g. "attack", "move", 
"build", "train a unit"). This means you can't recreate the game state (e.g.
unit positions, when units die, etc) without a perfect recreation of the game
mechanics.

