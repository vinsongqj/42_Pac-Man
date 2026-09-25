*This project has been created as part of the 42 curriculum by afomin, vgoh.*

# Pac-Man

## Description

42 Pac-Man is a project to recreate the popular game in Python, using object-oriented programming, a simple graphical library (pygame in our case), and a modular, reusable architecture. 

It supports:
*  A custom configuration via a file (JSON with comments) to set game parameters.
*  Level generation based on an external ‘A-Maze-ing‘ package provided by our peers.
*  A high-score system (stored in a database). # Specify more here later Alex
*  A polished graphical UI with main menu, game view, and game-over handling.
*  A cheat mode for evaluation purposes.
*  Deployment to a public gaming platform (Itch.io) for demonstration.

### Highscore

### Maze Generation

### Implementation

### General Software Architecture

## Instructions

A Makefile has been provided for convenience. You may choose to run the following commands:

```bash
make install       # Installs the dependencies required
make run           # Runs the game
make debug         # Debugs the program with python debugger
make lint          # Runs mypy and flake8 linting tests
make lint-strict   # Runs mypy with the --strict flag and flake8
make clean         # Removes all build files
```

Otherwise, if you would like to run the program manually, you may follow the steps below:
1. Install the dependencies with `uv sync`.
2. Run the program with `uv run pac-man.py config.json`.

### Configuration

## Project Management

## Resources

## Disclosure of AI Usage
