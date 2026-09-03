# Personal AI Agent — Bounded Autonomous Personal Operating Environment (V6.1)

A local-first, bounded autonomous personal AI agent operating system designed to execute multi-step missions across Gmail, Calendar, Tasks, Drive, Browser, and Local Files under strict safety and governance guarantees.

---

## 🔒 Core Invariants & Security Architecture

1. **Deterministic Safety Primacy**: *"No amount of intelligence can grant itself additional authority. The agent proposes, the AutonomyGovernor authorizes."*
2. **Zero-Bypass Master Architecture (V6.0)**: `PersonalAIOS_v6` master OS enforces zero-bypass safety across all 27 integrated sub-components.
3. **Temporal Lineage Immutability (V6.1)**: `TemporalKnowledgeGraph` past timeline events remain immutable historical facts while active status nodes update dynamically.
4. **Information Verification Invariant (V5.8)**: Externally acquired web research carrying `< 0.70` verification confidence CANNOT be directly ingested into RAG without explicit user validation.
5. **Prediction Non-Execution Invariant (V5.6)**: `PredictiveEventEngine` generates replanning risk warnings and completion probabilities, but CANNOT execute tool actions directly.
6. **Counterfactual Simulation Isolation (V5.7)**: `PersonalSimulationEnvironment` runs in an in-memory sandbox and NEVER mutates live state during simulation runs.
7. **User Preference Superseding Invariant (V5.3)**: `MemoryConflictResolver` enforces that newer explicit `USER` preferences 100% supersede older assertions.
8. **Authority-Intelligence Decoupling (V5.4)**: `AdaptiveModelSelector` optimizes intelligence routing, but `AutonomyGovernor` retains 100% authorization authority.
9. **Data Isolation & Secrets Protection**: OAuth tokens (`token.json`), client secrets (`credentials.json`), environment keys (`.env`), and personal memory databases are strictly gitignored and stay 100% private on local disk.

---

## 🧪 Testing & Verification

The codebase includes **1,127 unit tests** covering all 27 major architecture milestones from V0.1 to V6.1.

Run the complete test suite:
```bash
python -m unittest discover -s tests -p "test_v*.py"
```

Output:
```text
Ran 1127 tests in 3.716s
OK
```

---

## 🏃 Running the Agent

### Live Master Execution
```bash
python -m personal_agent
```

### Live Demo (Subsystems, Self-Improvement, Digital Twin, Autonomous Research & V6.0 Personal AI OS)
```bash
python scratch/demo_run_all.py
```
