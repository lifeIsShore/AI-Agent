# Personal Agent Security Specification — Hard Security Invariants

The security model of the Personal Agent Runtime is strictly non-negotiable. All tool invocations involving state mutations (`MODIFY` or `HIGH` risk level) must pass through the `PolicyEngine` security boundary.

```text
Memory ─────X────> Permission
```

---

## The 8 Hard Security Invariants

1. **Policy Authorization Required**: Every external `MODIFY` or mutating action strictly requires `PolicyEngine` authorization and explicit human approval when classified as `PENDING_APPROVAL`.
2. **Memory Cannot Grant Authority**: High preference confidence scores (`confidence=1.0`, `observations=100`) inform LLM reasoning and explainability (`why_proposed`), but NEVER grant tool execution authority without Policy Engine approval.
3. **No Direct User Override of Denied Actions**: User approval cannot transform a policy-denied proposal (`DENIED`) into an executable state without updating the system policy rules.
4. **TTL Expiration Enforcement**: Action proposals exceeding their TTL expiration timestamp (`expires_at`) automatically transition to `STATUS_EXPIRED` and block execution.
5. **Stale Target Re-validation**: Prior to tool execution, the target state must be re-validated (`target_validator`). If the target state changed out-of-band, execution is aborted.
6. **Proposal Origin Mandate**: Tool execution MUST originate from a registered `ActionProposal`. Direct or un-audited tool calls are strictly forbidden in production runtimes.
7. **Execution Instance Identity**: Every execution attempt must generate a unique `execution_id` (`exec_...`) distinct from the `proposal_id` (`prop_...`) and `idempotency_key`.
8. **Universal Accountability & Audit**: Every proposal creation, policy decision, approval, rejection, and execution result must be recorded to the append-only audit log (`data/logs/audit.jsonl`).
