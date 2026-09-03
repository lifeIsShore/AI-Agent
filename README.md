# Personal AI Agent — Bounded Autonomous Personal Operating Environment (V5.4)

A local-first, bounded autonomous personal AI agent operating system designed to execute multi-step missions across Gmail, Calendar, Tasks, Drive, Browser, and Local Files under strict safety and governance guarantees.

---

## 🔒 Core Invariants & Security Architecture

1. **Deterministic Safety Primacy**: *"No amount of intelligence can grant itself additional authority. The agent proposes, the AutonomyGovernor authorizes."*
2. **User Preference Superseding Invariant (V5.3)**: `MemoryConflictResolver` enforces that newer explicit `USER` preferences 100% supersede older explicit `USER` or `LEARNED` assertions.
3. **Memory Decay Protection (V5.3)**: Explicit `USER` preferences NEVER decay automatically over time.
4. **Authority-Intelligence Decoupling (V5.4)**: `AdaptiveModelSelector` optimizes intelligence routing based on task complexity, domain, preferences, and resource constraints, but `AutonomyGovernor` retains 100% authorization authority.
5. **Data Isolation & Secrets Protection**: OAuth tokens (`token.json`), client secrets (`credentials.json`), environment keys (`.env`), and personal memory databases are strictly gitignored and stay 100% private on local disk.

---

## 🧪 Testing & Verification

The codebase includes **812 unit tests** covering all 20 major architecture milestones from V0.1 to V5.4.

Run the complete test suite:
```bash
python -m unittest discover -s tests -p "test_v*.py"
```

Output:
```text
Ran 812 tests in 3.895s
OK
```

---

## 🏃 Running the Agent

### Live Master Execution
```bash
python -m personal_agent
```

### Live Demo (Subsystems, Self-Improvement, Memory Evolution & Adaptive Intelligence)
```bash
python scratch/demo_run_all.py
```
