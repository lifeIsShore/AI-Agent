# Personal AI Agent — Bounded Autonomous Personal Operating Environment (V5.0)

A local-first, bounded autonomous personal AI agent operating system designed to execute multi-step missions across Gmail, Calendar, Tasks, Drive, Browser, and Local Files under strict safety and governance guarantees.

---

## 🔒 Core Invariants & Security Architecture

1. **Deterministic Safety Primacy**: *"No amount of intelligence can grant itself additional authority. The agent proposes, the AutonomyGovernor authorizes."*
2. **Provenance Tracking**: 100% of consequential execution decisions track exact data origin, source system, confidence rating, timestamp, and deriving specialist agent.
3. **Data Isolation & Secrets Protection**: OAuth tokens (`token.json`), client secrets (`credentials.json`), environment keys (`.env`), and personal memory databases are strictly gitignored and stay 100% private on local disk.
4. **Bounded Self-Improvement**: The agent detects performance weaknesses and evaluates optimization candidates in an offline sandbox, but `ImprovementGovernor` strictly prohibits modifications to security boundaries, permissions, or governor rules.

---

## 🚀 Architecture Overview (V0.1 — V5.0)

```text
                  REAL-WORLD OPERATION
                          │
                          ▼
                 ┌─────────────────┐
                 │  MissionControl │
                 └────────┬────────┘
                          │
                 Personal World Model
                          │
        ┌─────────────────┼──────────────────┐
        ▼                 ▼                  ▼
     Memory            Event Bus          Context
        │                 │                  │
        └─────────────────┼──────────────────┘
                          ▼
                   Goal Arbitration
                          │
                          ▼
                Long-Horizon Planner
                          │
                          ▼
                     Agent Router
                          │
        ┌─────────┬──────┼──────┬─────────┐
        ▼         ▼      ▼      ▼         ▼
      Email    Research Calendar Browser Document
        │         │      │      │         │
        └─────────┴──────┼──────┴─────────┘
                         ▼
                    Model Router
                         │
                         ▼
                   Tool Execution
                         │
                         ▼
                 ┌───────────────┐
                 │Governor & Audit│
                 └───────┬───────┘
                         │
                         ▼
                Self-Improvement Sandbox
                         │
                         ▼
                    Verification
```

---

## 🧪 Testing & Verification

The codebase includes **632 unit tests** covering all 16 major architecture milestones from V0.1 to V5.0.

Run the complete test suite:
```bash
python -m unittest discover -s tests -p "test_v*.py"
```

Output:
```text
Ran 632 tests in 2.482s
OK
```

---

## 🏃 Running the Agent

### Live Master Execution
```bash
python -m personal_agent
```

### Live Demo (Subsystems & Self-Improvement Pipeline)
```bash
python scratch/demo_run_all.py
```

---

## 🔑 Setting Up Google Workspace Integration (Optional)

1. Obtain OAuth 2.0 Client Credentials from Google Cloud Console.
2. Save the credentials file to `credentials.json` in the root directory.
3. On first run, complete the OAuth sign-in flow.
4. The agent will create a dedicated task list titled **"AI Agent Tasks"** in your Google Tasks account.

*(Note: `credentials.json` and `token.json` are automatically ignored by Git and will never be committed or pushed to remote repositories).*
