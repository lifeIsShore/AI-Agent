import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from evals.security.prompt_injection import PromptInjectionEvaluator
from evals.security.policy_bypass import PolicyBypassEvaluator
from evals.security.memory_attacks import MemoryAttackEvaluator
from evals.security.privilege_escalation import PrivilegeEscalationEvaluator
from evals.security.data_exfiltration import DataExfiltrationEvaluator
from evals.security.identity_eval import IdentitySecurityEvaluator

def main():
    print("========================================")
    print("   V1.6 ADVERSARIAL SECURITY REPORT     ")
    print("========================================\n")

    pi_eval = PromptInjectionEvaluator()
    pb_eval = PolicyBypassEvaluator()
    ma_eval = MemoryAttackEvaluator()
    pe_eval = PrivilegeEscalationEvaluator()
    de_eval = DataExfiltrationEvaluator()
    id_eval = IdentitySecurityEvaluator()

    pi_res = pi_eval.evaluate_prompt_injections()
    pb_res = pb_eval.evaluate_policy_bypasses()
    ma_res = ma_eval.evaluate_memory_poisoning()
    pe_res = pe_eval.evaluate_privilege_escalation()
    de_res = de_eval.evaluate_data_exfiltration()
    id_res = id_eval.evaluate_identity_and_credentials()

    print("Identity & Authorization")
    print(f"  Tests:                    {id_res['total_identity_tests']}")
    print(f"  Unauthorized actions:      {id_res['unauthorized_actions']}\n")

    print("Credential Isolation")
    print(f"  Tests:                    {id_res['total_credential_tests']}")
    print(f"  Credential leaks:          {id_res['credential_leaks']}\n")

    print("Prompt Injection")
    print(f"  Tests:                    {pi_res['total_tests']}")
    print(f"  Successful bypasses:       {pi_res['successful_bypasses']}\n")

    print("Policy Enforcement")
    print(f"  Tests:                    {pb_res['total_tests']}")
    print(f"  Unauthorized executions:   {pb_res['unauthorized_executions']}\n")

    print("Memory Manipulation")
    print(f"  Tests:                    {ma_res['total_tests']}")
    print(f"  Unsafe memories stored:    {ma_res['unsafe_memories_stored']}\n")

    print("Privilege Escalation")
    print(f"  Tests:                    {pe_res['total_tests']}")
    print(f"  Escalations:               {pe_res['escalations']}\n")

    print("Data Exfiltration")
    print(f"  Tests:                    {de_res['total_tests']}")
    print(f"  Violations:                {de_res['violations']}\n")

    total_violations = (
        pi_res['successful_bypasses'] +
        pb_res['unauthorized_executions'] +
        ma_res['unsafe_memories_stored'] +
        pe_res['escalations'] +
        de_res['violations'] +
        id_res['unauthorized_actions'] +
        id_res['credential_leaks']
    )

    status = "PASS" if total_violations == 0 else "FAIL"
    print("========================================")
    print(f" SECURITY STATUS: {status}")
    print("========================================")

if __name__ == "__main__":
    main()
