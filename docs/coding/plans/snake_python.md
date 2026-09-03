# Mission: Build Snake Game — Python

## 1. Objective

Create a complete playable Snake game in Python.

The game must run locally without requiring an internet connection.

Use a simple graphical interface.

## 2. Technology Constraints

Use:

* Python 3
* Pygame

Do NOT use:

* external web APIs
* databases
* network connections
* AI/LLM APIs
* unnecessary frameworks
* complex architecture

Install only the minimum dependency required.

Expected dependency:

```text
pygame
```

## 3. Workspace

Create the project inside the designated CodingAgent sandbox.

Do NOT modify unrelated files in the main AI-Agent project.

Recommended project directory:

```text
coding_workspaces/sandbox/snake_python/
```

Expected structure:

```text
snake_python/
├── main.py
├── requirements.txt
├── README.md
└── tests/
    └── test_game_logic.py
```

Keep the implementation small and easy to understand.

## 4. Game Requirements

Implement a classic Snake game.

### Board

Use a fixed grid.

Recommended:

```text
GRID_WIDTH = 30
GRID_HEIGHT = 20
CELL_SIZE = 25
```

Window size should therefore be:

```text
750 x 500
```

### Snake

The snake must:

* start near the center
* contain multiple segments
* move continuously
* move one grid cell at a time
* grow after eating food
* have a visible head and body

### Controls

Use:

```text
UP
DOWN
LEFT
RIGHT
```

Keyboard controls:

```text
Arrow Up
Arrow Down
Arrow Left
Arrow Right
```

Also support:

```text
W
A
S
D
```

Do not allow an immediate 180-degree reversal.

For example:

```text
RIGHT → LEFT
```

must be ignored.

## 5. Food

Generate food at a random free grid position.

Food must NOT spawn inside the snake.

When the snake eats food:

1. increase score
2. increase snake length
3. generate new food

## 6. Collision Detection

The game ends when:

### Wall collision

Snake head leaves the board.

### Self collision

Snake head touches the snake body.

Do not treat the snake's normal movement into its previous tail position as a collision if that tail segment is removed during the same movement.

Keep collision logic simple and deterministic.

## 7. Score

Display the score at the top of the window.

Example:

```text
Score: 10
```

Increase score by:

```text
+1
```

for every food item eaten.

## 8. Game Over

When the game ends:

* stop normal movement
* display `GAME OVER`
* display final score
* provide a restart instruction

Example:

```text
GAME OVER
Score: 12

Press R to restart
Press ESC to quit
```

## 9. Restart

Pressing `R` after game over must:

* reset the snake
* reset score
* generate new food
* restart movement
* return to the normal playing state

## 10. Quit

Pressing `ESC` must close the game.

Closing the window must also terminate cleanly.

## 11. Game States

Use a simple state model:

```text
PLAYING
GAME_OVER
```

Do not create an unnecessarily complicated state architecture.

## 12. Code Organization

Prefer small functions/classes.

Recommended responsibilities:

```text
Snake
Food
Game
```

Possible methods:

```text
Snake.move()
Snake.grow()
Snake.change_direction()

Game.reset()
Game.handle_events()
Game.update()
Game.draw()
Game.run()
```

Do not over-engineer the implementation.

## 13. Deterministic Game Logic

Separate game logic from rendering where practical.

The following logic should be easy to test:

* movement
* direction changes
* food consumption
* growth
* wall collision
* self collision
* score updates

## 14. Testing

Create unit tests for the game logic.

At minimum test:

1. snake moves correctly
2. direction changes correctly
3. opposite direction is rejected
4. snake grows after food consumption
5. score increases after food consumption
6. wall collision is detected
7. self collision is detected
8. restart resets game state

Tests must NOT require opening a graphical game window.

If Pygame initialization makes testing difficult, isolate pure game logic from rendering.

## 15. Requirements File

Create:

```text
requirements.txt
```

containing only the required dependency.

Example:

```text
pygame
```

Do not add unnecessary packages.

## 16. README

Create a short README containing:

* project description
* requirements
* installation instructions
* run instructions
* controls
* testing instructions

Example commands should be:

```bash
python -m pip install -r requirements.txt
python main.py
```

Tests:

```bash
python -m unittest discover -s tests
```

## 17. CodingAgent Workflow

Follow this exact workflow:

```text
1. Inspect workspace
2. Create project structure
3. Implement game logic
4. Implement rendering
5. Implement input handling
6. Implement restart/game-over behavior
7. Create tests
8. Run tests
9. Fix failures
10. Run tests again
11. Inspect final files
12. Produce git diff
13. Produce implementation summary
```

Do NOT skip testing.

## 18. Safety Constraints

The CodingAgent must:

* work only inside the assigned Snake workspace
* not access unrelated personal files
* not access credentials
* not access browser passwords
* not modify the AI-Agent production system
* not delete unrelated files
* not perform deployment
* not install system-wide software
* not execute destructive Git operations

## 19. Completion Criteria

The mission is complete only when:

* [ ] Snake launches successfully
* [ ] Snake moves
* [ ] Arrow keys work
* [ ] WASD works
* [ ] Food appears
* [ ] Food cannot spawn inside snake
* [ ] Snake grows
* [ ] Score increases
* [ ] Wall collision works
* [ ] Self collision works
* [ ] 180-degree reversal is prevented
* [ ] Game over works
* [ ] Restart works
* [ ] ESC exits
* [ ] Unit tests pass
* [ ] README exists
* [ ] requirements.txt exists
* [ ] final diff is clean and understandable

## 20. Final Report

After completion, report:

```text
Implementation:
- files created
- files modified
- main features

Testing:
- number of tests
- passed
- failed

Execution:
- command used to launch game

Security:
- workspace used
- capabilities used
- permissions requested

Git:
- files changed
- diff summary

Status:
SUCCESS / FAILED
```

Do not claim success unless the tests and execution checks actually pass.
