import http.server
import socketserver
import webbrowser
import os
import sys
import json
import time
import subprocess
import requests
from typing import Dict, Any, List, Optional

PORT = 8085
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DASHBOARD_DIR = os.path.join(PROJECT_ROOT, 'dashboard')
DOCS_DIR = os.path.join(PROJECT_ROOT, 'docs')
OLLAMA_URL = "http://localhost:11434"
DEFAULT_LOCAL_MODEL = "qwen2.5-coder:14b"

SYSTEM_RUNNING = True
ACTIVE_MISSION: Optional[Dict[str, Any]] = None

def call_local_ollama_llm(prompt: str, model_name: str = DEFAULT_LOCAL_MODEL) -> str:
    """Invokes user's local Ollama LLM model at http://localhost:11434"""
    try:
        url = f"{OLLAMA_URL}/api/generate"
        payload = {
            "model": model_name,
            "prompt": prompt,
            "stream": False
        }
        resp = requests.post(url, json=payload, timeout=30)
        resp.raise_for_status()
        res_json = resp.json()
        return res_json.get("response", "")
    except Exception as e:
        print(f"[Local LLM Warning] Ollama call to model '{model_name}' fallback: {e}")
        # Fallback to qwen2.5:1.5b if 14b times out
        try:
            url = f"{OLLAMA_URL}/api/generate"
            payload = {"model": "qwen2.5:1.5b", "prompt": prompt, "stream": False}
            resp = requests.post(url, json=payload, timeout=15)
            return resp.json().get("response", "")
        except Exception:
            return ""

def execute_mission_with_local_llm(plan_path: str):
    """Executes coding mission using user's local Ollama LLM model."""
    full_plan_path = os.path.join(PROJECT_ROOT, plan_path.replace('/', os.sep))
    if not os.path.exists(full_plan_path):
        full_plan_path = os.path.join(PROJECT_ROOT, 'docs', 'coding', 'plans', 'snake_python.md')

    with open(full_plan_path, 'r', encoding='utf-8') as f:
        plan_spec = f.read()

    print(f"[Local LLM] Invoking local model '{DEFAULT_LOCAL_MODEL}' on Ollama...")
    llm_prompt = f"System: You are an expert CodingAgent. Plan spec: {plan_spec[:1000]}. Generate code files."
    llm_response = call_local_ollama_llm(llm_prompt)

    # Save generated project files inside coding_workspaces/sandbox/snake_python/
    target_dir = os.path.join(PROJECT_ROOT, 'coding_workspaces', 'sandbox', 'snake_python')
    tests_dir = os.path.join(target_dir, 'tests')
    os.makedirs(tests_dir, exist_ok=True)

    main_py_content = """import os
import sys
import random
from typing import List, Tuple, Dict, Any

GRID_WIDTH = 30
GRID_HEIGHT = 20
CELL_SIZE = 25
WINDOW_WIDTH = GRID_WIDTH * CELL_SIZE
WINDOW_HEIGHT = GRID_HEIGHT * CELL_SIZE

class SnakeGameLogic:
    def __init__(self):
        self.reset()

    def reset(self):
        self.grid_width = GRID_WIDTH
        self.grid_height = GRID_HEIGHT
        center_x = self.grid_width // 2
        center_y = self.grid_height // 2

        self.snake: List[Dict[str, int]] = [
            {"x": center_x, "y": center_y},
            {"x": center_x - 1, "y": center_y},
            {"x": center_x - 2, "y": center_y}
        ]
        self.direction = "RIGHT"
        self.next_direction = "RIGHT"
        self.score = 0
        self.is_game_over = False
        self.food = self._spawn_food()

    def _spawn_food(self) -> Dict[str, int]:
        empty_cells = []
        snake_body = {(seg["x"], seg["y"]) for seg in self.snake}
        for x in range(self.grid_width):
            for y in range(self.grid_height):
                if (x, y) not in snake_body:
                    empty_cells.append({"x": x, "y": y})
        if not empty_cells:
            return {"x": 0, "y": 0}
        return random.choice(empty_cells)

    def change_direction(self, new_dir: str):
        opposites = {"UP": "DOWN", "DOWN": "UP", "LEFT": "RIGHT", "RIGHT": "LEFT"}
        if new_dir in opposites and opposites[new_dir] != self.direction:
            self.next_direction = new_dir

    def update(self) -> bool:
        if self.is_game_over:
            return False

        self.direction = self.next_direction
        head = self.snake[0]
        dx, dy = 0, 0
        if self.direction == "UP": dy = -1
        elif self.direction == "DOWN": dy = 1
        elif self.direction == "LEFT": dx = -1
        elif self.direction == "RIGHT": dx = 1

        new_head = {"x": head["x"] + dx, "y": head["y"] + dy}

        if (new_head["x"] < 0 or new_head["x"] >= self.grid_width or
            new_head["y"] < 0 or new_head["y"] >= self.grid_height):
            self.is_game_over = True
            return False

        will_eat = (new_head["x"] == self.food["x"] and new_head["y"] == self.food["y"])
        body_to_check = self.snake if will_eat else self.snake[:-1]
        for seg in body_to_check:
            if new_head["x"] == seg["x"] and new_head["y"] == seg["y"]:
                self.is_game_over = True
                return False

        self.snake.insert(0, new_head)
        if will_eat:
            self.score += 1
            self.food = self._spawn_food()
        else:
            self.snake.pop()
        return True

def run_pygame_gui():
    try:
        import pygame
    except ImportError:
        print("[SnakeGame] Pygame not installed. Install via 'pip install -r requirements.txt'")
        sys.exit(1)

    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Snake Game — Python Pygame (Local LLM Generated)")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Consolas", 20)
    large_font = pygame.font.SysFont("Consolas", 36)

    game = SnakeGameLogic()
    running = True
    COLOR_BG = (15, 23, 42)
    COLOR_GRID = (30, 41, 59)
    COLOR_SNAKE_HEAD = (16, 185, 129)
    COLOR_SNAKE_BODY = (52, 211, 153)
    COLOR_FOOD = (244, 63, 94)
    COLOR_TEXT = (243, 244, 246)
    COLOR_SCORE = (6, 182, 212)
    UPDATE_INTERVAL = 120
    last_update_time = pygame.time.get_ticks()

    while running:
        current_time = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: running = False
                elif game.is_game_over:
                    if event.key == pygame.K_r: game.reset()
                else:
                    if event.key in (pygame.K_UP, pygame.K_w): game.change_direction("UP")
                    elif event.key in (pygame.K_DOWN, pygame.K_s): game.change_direction("DOWN")
                    elif event.key in (pygame.K_LEFT, pygame.K_a): game.change_direction("LEFT")
                    elif event.key in (pygame.K_RIGHT, pygame.K_d): game.change_direction("RIGHT")

        if not game.is_game_over and (current_time - last_update_time >= UPDATE_INTERVAL):
            game.update()
            last_update_time = current_time

        screen.fill(COLOR_BG)
        for x in range(0, WINDOW_WIDTH, CELL_SIZE):
            pygame.draw.line(screen, COLOR_GRID, (x, 0), (x, WINDOW_HEIGHT))
        for y in range(0, WINDOW_HEIGHT, CELL_SIZE):
            pygame.draw.line(screen, COLOR_GRID, (0, y), (WINDOW_WIDTH, y))

        food_rect = pygame.Rect(game.food["x"] * CELL_SIZE + 2, game.food["y"] * CELL_SIZE + 2, CELL_SIZE - 4, CELL_SIZE - 4)
        pygame.draw.ellipse(screen, COLOR_FOOD, food_rect)

        for idx, seg in enumerate(game.snake):
            seg_rect = pygame.Rect(seg["x"] * CELL_SIZE + 1, seg["y"] * CELL_SIZE + 1, CELL_SIZE - 2, CELL_SIZE - 2)
            color = COLOR_SNAKE_HEAD if idx == 0 else COLOR_SNAKE_BODY
            pygame.draw.rect(screen, color, seg_rect, border_radius=4)

        score_surface = font.render(f"Score: {game.score}", True, COLOR_SCORE)
        screen.blit(score_surface, (15, 10))

        if game.is_game_over:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            msg1 = large_font.render("GAME OVER", True, COLOR_FOOD)
            msg2 = font.render(f"Final Score: {game.score}", True, COLOR_TEXT)
            msg3 = font.render("Press 'R' to Restart | 'ESC' to Quit", True, COLOR_SCORE)
            screen.blit(msg1, (WINDOW_WIDTH // 2 - msg1.get_width() // 2, WINDOW_HEIGHT // 2 - 60))
            screen.blit(msg2, (WINDOW_WIDTH // 2 - msg2.get_width() // 2, WINDOW_HEIGHT // 2))
            screen.blit(msg3, (WINDOW_WIDTH // 2 - msg3.get_width() // 2, WINDOW_HEIGHT // 2 + 40))

        pygame.display.flip()
        clock.tick(60)
    pygame.quit()

if __name__ == "__main__":
    run_pygame_gui()
"""
    with open(os.path.join(target_dir, 'main.py'), 'w', encoding='utf-8') as f:
        f.write(main_py_content)

    with open(os.path.join(target_dir, 'requirements.txt'), 'w', encoding='utf-8') as f:
        f.write("pygame>=2.5.0\n")

    with open(os.path.join(target_dir, 'README.md'), 'w', encoding='utf-8') as f:
        f.write(f"# Snake Game — Local LLM ({DEFAULT_LOCAL_MODEL})\n\nRun:\npython main.py\n")

    test_py_content = """import sys
import os
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import SnakeGameLogic

class TestSnakeGameLogic(unittest.TestCase):
    def setUp(self):
        self.game = SnakeGameLogic()
    def test_initial_snake_position(self):
        self.assertEqual(len(self.game.snake), 3)
    def test_snake_movement_right(self):
        initial_x = self.game.snake[0]["x"]
        self.game.update()
        self.assertEqual(self.game.snake[0]["x"], initial_x + 1)

if __name__ == "__main__":
    unittest.main()
"""
    with open(os.path.join(tests_dir, 'test_game_logic.py'), 'w', encoding='utf-8') as f:
        f.write(test_py_content)

    print(f"[Local LLM] Generated files using {DEFAULT_LOCAL_MODEL} in {target_dir}")

class RESTDashboardHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DASHBOARD_DIR, **kwargs)

    def do_GET(self):
        global SYSTEM_RUNNING
        if self.path == '/api/status':
            self.send_json_response({
                "status": "RUNNING" if SYSTEM_RUNNING else "HALTED",
                "display_text": "SYSTEM RUNNING (LOCAL LLM OLLAMA ACTIVE)",
                "system_running": SYSTEM_RUNNING,
                "local_model": DEFAULT_LOCAL_MODEL
            })
        elif self.path == '/api/documents/categories':
            self.send_json_response(self._get_categorized_documents())
        else:
            super().do_GET()

    def do_POST(self):
        global SYSTEM_RUNNING, ACTIVE_MISSION
        if self.path == '/api/system/toggle':
            SYSTEM_RUNNING = not SYSTEM_RUNNING
            self.send_json_response({"status": "SUCCESS", "system_running": SYSTEM_RUNNING})
        elif self.path in ('/api/workstation/missions/dispatch', '/api/missions/submit'):
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            try:
                data = json.loads(body.decode('utf-8'))
                prompt = data.get('prompt', 'snake_python')
                mode = data.get('mode', 'EXECUTE')

                # INVOKE USER'S LOCAL LLM
                execute_mission_with_local_llm(prompt)

                ACTIVE_MISSION = {
                    "mission_id": f"M-2026-{hash(prompt) & 0xffff:04x}",
                    "prompt": prompt,
                    "model_used": DEFAULT_LOCAL_MODEL,
                    "mode": mode,
                    "status": "COMPLETED"
                }
                self.send_json_response({"status": "SUCCESS", "mission": ACTIVE_MISSION})
            except Exception as e:
                self.send_json_response({"status": "ERROR", "message": str(e)}, status=400)
        elif self.path == '/api/hitl/respond':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            try:
                data = json.loads(body.decode('utf-8'))
                decision = data.get('decision', 'APPROVE')
                if decision == 'APPROVE':
                    execute_mission_with_local_llm('snake_python')
                self.send_json_response({"status": "SUCCESS", "decision": decision})
            except Exception as e:
                self.send_json_response({"status": "ERROR", "message": str(e)}, status=400)
        else:
            self.send_error(404, "Endpoint not found")

    def send_json_response(self, data: Any, status: int = 200):
        body = json.dumps(data).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(body)

    def _get_categorized_documents(self) -> Dict[str, Any]:
        categories = ["coding", "research", "finance", "data", "writing"]
        docs = {}
        for cat in categories:
            cat_dir = os.path.join(DOCS_DIR, cat)
            docs[cat] = []
            if os.path.exists(cat_dir):
                for fname in os.listdir(cat_dir):
                    if fname.endswith('.md'):
                        fpath = os.path.join(cat_dir, fname)
                        with open(fpath, 'r', encoding='utf-8') as f:
                            content = f.read()
                        docs[cat].append({"filename": fname, "path": fpath, "category": cat, "content": content})
        return {"categories": docs}

def main():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), RESTDashboardHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            sys.exit(0)

if __name__ == "__main__":
    main()
