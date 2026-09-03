# Personal AI Agent — Bounded Autonomous Personal Operating Environment (V5.7)

A local-first, bounded autonomous personal AI agent operating system designed to execute multi-step missions across Gmail, Calendar, Tasks, Drive, Browser, and Local Files under strict safety and governance guarantees.

---

## 🔒 Core Invariants & Security Architecture

1. **Deterministic Safety Primacy**: *"No amount of intelligence can grant itself additional authority. The agent proposes, the AutonomyGovernor authorizes."*
2. **Prediction Non-Execution Invariant (V5.6)**: `PredictiveEventEngine` generates replanning risk warnings and completion probabilities, but CANNOT execute tool actions directly.
3. **Counterfactual Simulation Isolation (V5.7)**: `PersonalSimulationEnvironment` runs in an in-memory sandbox and NEVER mutates live state, database files, or external services during simulation runs.
4. **User Preference Superseding Invariant (V5.3)**: `MemoryConflictResolver` enforces that newer explicit `USER` preferences 100% supersede older assertions.
5. **Authority-Intelligence Decoupling (V5.4)**: `AdaptiveModelSelector` optimizes intelligence routing, but `AutonomyGovernor` retains 100% authorization authority.
6. **Data Isolation & Secrets Protection**: OAuth tokens (`token.json`), client secrets (`credentials.json`), environment keys (`.env`), and personal memory databases are strictly gitignored and stay 100% private on local disk.

---

## 🧪 Testing & Verification

The codebase includes **947 unit tests** covering all 23 major architecture milestones from V0.1 to V5.7.

Run the complete test suite:
```bash
python -m unittest discover -s tests -p "test_v*.py"
```

Output:
```text
Ran 947 tests in 3.014s
OK
```

---

## 🏃 Running the Agent

### Live Master Execution
```bash
python -m personal_agent
```

### Live Demo (Subsystems, Self-Improvement, Predictions & Digital Twin Sandbox)
```bash
python scratch/demo_run_all.py
```
