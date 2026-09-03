# Mission: Build Snake Game — HTML/CSS/JavaScript

## 1. Objective

Create a complete playable Snake game that runs locally in a web browser.

The game must work without an internet connection.

## 2. Technology Constraints

Use only:

* HTML5
* CSS3
* vanilla JavaScript

Do NOT use:

* React
* Vue
* Angular
* Bootstrap
* Tailwind
* jQuery
* external JavaScript libraries
* external CSS libraries
* web APIs requiring authentication
* backend servers

The project must be completely self-contained.

## 3. Workspace

Create the project inside:

```text
coding_workspaces/sandbox/snake_web/
```

Do not modify unrelated files.

Expected structure:

```text
snake_web/
├── index.html
├── style.css
├── game.js
└── README.md
```

Optional:

```text
snake_web/
└── tests/
```

Keep the project simple.

## 4. HTML Structure

Create a page containing:

* game title
* score display
* game board
* game-over message
* restart button/instruction
* short controls section

Use semantic HTML where reasonable.

The game board may use:

```text
HTML Canvas
```

Canvas is preferred for simple rendering.

Recommended:

```text
canvas width = 750
canvas height = 500
```

## 5. Game Grid

Use:

```text
GRID_WIDTH = 30
GRID_HEIGHT = 20
CELL_SIZE = 25
```

The coordinate system should use integer grid positions.

Example:

```text
x = 0 ... 29
y = 0 ... 19
```

## 6. Snake

The snake must:

* start near the center
* contain multiple segments
* move continuously
* move one grid cell per update
* grow when eating food

Represent the snake using a simple JavaScript array.

Example conceptual structure:

```text
[
  {x: 15, y: 10},
  {x: 14, y: 10},
  {x: 13, y: 10}
]
```

## 7. Controls

Support:

```text
ArrowUp
ArrowDown
ArrowLeft
ArrowRight
```

Also support:

```text
W
A
S
D
```

Prevent immediate 180-degree reversal.

Example:

```text
RIGHT → LEFT
```

must be rejected.

## 8. Food

Generate food randomly on an empty grid position.

Food must never spawn on an existing snake segment.

When food is eaten:

1. increase score
2. grow snake
3. generate new food

## 9. Collision Detection

Detect:

### Wall collision

Snake head leaves the board.

### Self collision

Snake head touches another snake segment.

Keep collision logic deterministic and easy to understand.

## 10. Score

Display:

```text
Score: 0
```

Increase by one for every food item eaten.

Update the DOM whenever the score changes.

## 11. Game Over

When collision occurs:

* stop the game loop
* display a game-over message
* display final score
* allow restart

Example:

```text
GAME OVER

Score: 12

Press R or click Restart
```

## 12. Restart

Provide a visible:

```text
Restart
```

button.

Also support:

```text
R
```

Restart must reset:

* snake
* direction
* score
* food
* game state

## 13. Game State

Use a simple state:

```text
playing = true/false
```

or an equivalent simple state representation.

Avoid unnecessary state-management frameworks.

## 14. Rendering

Use HTML Canvas.

Every frame/update:

1. clear canvas
2. draw food
3. draw snake
4. update score/UI

Keep rendering functions separate from game logic.

Recommended functions:

```text
drawBoard()
drawSnake()
drawFood()
drawGameOver()
```

## 15. Game Loop

Use a simple timer/game loop.

The game should:

* update at a consistent interval
* move the snake
* check collisions
* check food
* render the new state

Do not make the game unnecessarily fast.

Recommended initial movement interval:

```text
120 ms
```

## 16. Input Handling

Keyboard input must be event-driven.

Do not poll the keyboard continuously.

When a key is pressed:

1. identify requested direction
2. verify it is not the opposite direction
3. update direction

Prevent multiple invalid direction changes from causing immediate reversal.

## 17. Responsive Presentation

The game should be visually clean.

Include:

* centered game container
* clear title
* visible score
* visible canvas
* restart control
* readable controls

Do not spend excessive effort on complex visual effects.

The priority is functionality.

## 18. Browser Compatibility

The game should work in a modern desktop browser.

No build step should be required.

The user should be able to open:

```text
index.html
```

directly.

If direct file execution causes a browser restriction, provide an optional simple local-server command in the README.

Do NOT introduce a Node.js build system unless necessary.

## 19. README

Create a README containing:

* project description
* file structure
* how to run
* controls
* gameplay description
* testing/checking instructions

Preferred launch method:

```text
Open index.html in a modern browser.
```

Optional:

```bash
python -m http.server 8000
```

Then open:

```text
http://localhost:8000
```

## 20. Testing / Verification

Because this is a small vanilla JavaScript project, perform at least:

### Static checks

Verify:

* all referenced files exist
* no missing JavaScript imports
* no missing CSS references
* no syntax errors

### Functional verification

Verify:

1. page loads
2. canvas appears
3. snake appears
4. snake moves
5. Arrow keys work
6. WASD works
7. food appears
8. food is not placed on snake
9. eating food increases score
10. snake grows
11. wall collision causes game over
12. self collision causes game over
13. opposite direction is rejected
14. restart works
15. R works
16. no console errors occur during normal play

If browser automation is available, use it for verification.

Otherwise, provide a clear manual verification checklist.

## 21. CodingAgent Workflow

Follow:

```text
1. Inspect workspace
2. Create HTML/CSS/JS structure
3. Implement game state
4. Implement movement
5. Implement collision detection
6. Implement food
7. Implement scoring
8. Implement rendering
9. Implement controls
10. Implement game-over/restart
11. Run static checks
12. Run browser verification if available
13. Inspect files
14. Produce final diff
15. Produce implementation report
```

## 22. Safety Constraints

The CodingAgent must:

* operate only inside the assigned Snake workspace
* not modify unrelated AI-Agent files
* not access credentials
* not access personal files outside the workspace
* not install unnecessary software
* not deploy the application
* not perform destructive Git operations

## 23. Completion Criteria

The mission is complete only when:

* [ ] index.html exists
* [ ] style.css exists
* [ ] game.js exists
* [ ] README.md exists
* [ ] page loads
* [ ] game board appears
* [ ] snake moves
* [ ] keyboard controls work
* [ ] food works
* [ ] scoring works
* [ ] growth works
* [ ] wall collision works
* [ ] self collision works
* [ ] reverse direction is blocked
* [ ] game over works
* [ ] restart works
* [ ] no normal-play console errors
* [ ] final diff is clean

## 24. Final Report

Report:

```text
Implementation:
- files created
- files modified
- features implemented

Verification:
- static checks
- browser checks
- manual checks if applicable

Security:
- workspace used
- capabilities used
- permissions requested

Git:
- changed files
- diff summary

Status:
SUCCESS / FAILED
```

Do not claim success unless verification was actually performed.
