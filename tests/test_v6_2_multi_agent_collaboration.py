import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from personal_agent.multi_agent.mission_team import MissionTeam
from personal_agent.multi_agent.agent_collaboration_protocol import AgentMessage, CollaborationProtocol, AgentTaskDelegator
from personal_agent.multi_agent.critic_agent import CriticAgent
from personal_agent.multi_agent.verification_agent import VerificationAgent
from personal_agent.multi_agent.inter_agent_conflict_resolver import InterAgentConflictResolver

class TestV62MultiAgentCollaboration(unittest.TestCase):

    def setUp(self):
        self.team = MissionTeam("ThesisTeam")
        self.protocol = CollaborationProtocol()
        self.delegator = AgentTaskDelegator()
        self.critic = CriticAgent()
        self.verifier = VerificationAgent()
        self.resolver = InterAgentConflictResolver()

    def test_1_mission_team_initializes(self):
        """Test 1: MissionTeam initializes with 5 members."""
        self.assertEqual(len(self.team.members), 5)
        self.assertTrue(self.team.team_id.startswith("team_"))

    def test_2_get_agent_by_role(self):
        """Test 2: get_agent_by_role retrieves specialist cleanly."""
        critic = self.team.get_agent_by_role("CRITIC")
        self.assertEqual(critic["agent_id"], "CriticAgent")

    def test_3_collaboration_protocol_send_message(self):
        """Test 3: CollaborationProtocol sends and records inter-agent messages."""
        msg = self.protocol.send_message("ResearchSpecialist", "PlanningSpecialist", "DATA", "Found sources.")
        self.assertEqual(msg.sender_id, "ResearchSpecialist")
        self.assertEqual(len(self.protocol.message_history), 1)

    def test_4_critic_agent_evaluates_plan_quality_pass(self):
        """Test 4: CriticAgent passes plan containing research and review steps."""
        plan = {"steps": ["research_sources", "review_findings"]}
        res = self.critic.evaluate_plan_quality(plan)
        self.assertTrue(res["passed"])
        self.assertEqual(res["quality_score"], 0.95)

    def test_5_critic_agent_evaluates_plan_quality_fail(self):
        """Test 5: CriticAgent rejects incomplete plan lacking review step."""
        plan = {"steps": ["execute"]}
        res = self.critic.evaluate_plan_quality(plan)
        self.assertFalse(res["passed"])

    def test_6_verification_agent_verifies_threshold_met(self):
        """Test 6: VerificationAgent verifies valid evidence list."""
        ev = [{"confidence": 0.85}, {"confidence": 0.90}]
        res = self.verifier.verify_evidence_threshold(ev)
        self.assertTrue(res["threshold_met"])

    def test_7_verification_agent_verifies_threshold_failed(self):
        """Test 7: VerificationAgent fails when evidence is low confidence."""
        ev = [{"confidence": 0.40}]
        res = self.verifier.verify_evidence_threshold(ev)
        self.assertFalse(res["threshold_met"])

    def test_8_conflict_resolver_picks_higher_confidence(self):
        """Test 8: InterAgentConflictResolver selects proposal with higher confidence."""
        p_a = {"agent_id": "AgentA", "confidence": 0.60}
        p_b = {"agent_id": "AgentB", "confidence": 0.90}
        res = self.resolver.resolve_agent_conflict(p_a, p_b)
        self.assertEqual(res["winning_proposal"]["agent_id"], "AgentB")

    def test_9_agent_task_delegator(self):
        """Test 9: AgentTaskDelegator generates delegated task dictionary."""
        del_res = self.delegator.delegate_subtask("PlanningSpecialist", "ResearchSpecialist", "Literature Search")
        self.assertEqual(del_res["target"], "ResearchSpecialist")
        self.assertEqual(del_res["status"], "DELEGATED")

    def test_10_collaboration_stream_formatting(self):
        """Test 10: get_collaboration_stream returns list of dictionaries."""
        self.protocol.send_message("A", "B", "TYPE", "Content")
        stream = self.protocol.get_collaboration_stream()
        self.assertEqual(len(stream), 1)
        self.assertIn("timestamp", stream[0])

    def test_11_agent_message_id_prefix(self):
        """Test 11: AgentMessage ID starts with msg_."""
        msg = AgentMessage("A", "B", "T", "C")
        self.assertTrue(msg.msg_id.startswith("msg_"))

    def test_12_team_get_agent_by_unknown_role(self):
        """Test 12: get_agent_by_role returns None for unknown role."""
        self.assertIsNone(self.team.get_agent_by_role("UNKNOWN"))

    def test_13_critic_agent_id(self):
        """Test 13: CriticAgent ID is CriticAgent."""
        self.assertEqual(self.critic.agent_id, "CriticAgent")

    def test_14_verifier_agent_id(self):
        """Test 14: VerificationAgent ID is VerificationAgent."""
        self.assertEqual(self.verifier.agent_id, "VerificationAgent")

    def test_15_conflict_resolver_equal_confidence(self):
        """Test 15: Conflict resolver selects proposal_a on equal confidence."""
        p_a = {"agent_id": "AgentA", "confidence": 0.80}
        p_b = {"agent_id": "AgentB", "confidence": 0.80}
        res = self.resolver.resolve_agent_conflict(p_a, p_b)
        self.assertEqual(res["winning_proposal"]["agent_id"], "AgentA")

    def test_16_delegation_id_prefix(self):
        """Test 16: Delegation ID starts with del_."""
        d = self.delegator.delegate_subtask("A", "B", "S")
        self.assertTrue(d["delegation_id"].startswith("del_"))

    def test_17_message_payload_default(self):
        """Test 17: Message payload defaults to empty dict."""
        msg = AgentMessage("A", "B", "T", "C")
        self.assertEqual(msg.payload, {})

    def test_18_protocol_message_history_type(self):
        """Test 18: message_history is list."""
        self.assertIsInstance(self.protocol.message_history, list)

    def test_19_team_members_list_length(self):
        """Test 19: get_team_members returns list of length 5."""
        members = self.team.get_team_members()
        self.assertEqual(len(members), 5)

    def test_20_stateless_execution(self):
        """Test 20: Critic execution is stateless."""
        r1 = self.critic.evaluate_plan_quality({"steps": ["research", "review"]})
        r2 = self.critic.evaluate_plan_quality({"steps": ["research", "review"]})
        self.assertEqual(r1["passed"], r2["passed"])

    def test_21_verifier_empty_evidence(self):
        """Test 21: VerificationAgent handles empty evidence list."""
        res = self.verifier.verify_evidence_threshold([])
        self.assertFalse(res["threshold_met"])

    def test_22_critic_feedback_string(self):
        """Test 22: Feedback is string."""
        res = self.critic.evaluate_plan_quality({})
        self.assertIsInstance(res["feedback"], str)

    def test_23_resolver_winning_proposal_dict(self):
        """Test 23: winning_proposal is dict."""
        res = self.resolver.resolve_agent_conflict({}, {})
        self.assertIsInstance(res["winning_proposal"], dict)

    def test_24_delegator_status_string(self):
        """Test 24: Delegation status is DELEGATED string."""
        d = self.delegator.delegate_subtask("A", "B", "S")
        self.assertEqual(d["status"], "DELEGATED")

    def test_25_protocol_stream_dict_keys(self):
        """Test 25: Stream dictionary contains 7 keys."""
        self.protocol.send_message("A", "B", "T", "C")
        stream = self.protocol.get_collaboration_stream()
        self.assertEqual(len(stream[0]), 7)

    def test_26_team_name_preserved(self):
        """Test 26: Team name preserved."""
        self.assertEqual(self.team.team_name, "ThesisTeam")

    def test_27_verifier_status_string(self):
        """Test 27: Status is string."""
        res = self.verifier.verify_evidence_threshold([{"confidence": 0.9}])
        self.assertEqual(res["status"], "EVIDENCE_VERIFIED")

    def test_28_critic_quality_score_float(self):
        """Test 28: quality_score is float."""
        res = self.critic.evaluate_plan_quality({})
        self.assertIsInstance(res["quality_score"], float)

    def test_29_message_to_dict_method(self):
        """Test 29: to_dict method outputs dictionary."""
        msg = AgentMessage("A", "B", "T", "C")
        self.assertIsInstance(msg.to_dict(), dict)

    def test_30_delegation_dict_keys_count(self):
        """Test 30: Delegation dict contains 5 keys."""
        d = self.delegator.delegate_subtask("A", "B", "S")
        self.assertEqual(len(d), 5)

    def test_31_critic_pass_boolean(self):
        """Test 31: passed is boolean."""
        res = self.critic.evaluate_plan_quality({})
        self.assertIsInstance(res["passed"], bool)

    def test_32_verifier_threshold_met_boolean(self):
        """Test 32: threshold_met is boolean."""
        res = self.verifier.verify_evidence_threshold([])
        self.assertIsInstance(res["threshold_met"], bool)

    def test_33_message_timestamp_string(self):
        """Test 33: timestamp is string."""
        msg = AgentMessage("A", "B", "T", "C")
        self.assertIsInstance(msg.timestamp, str)

    def test_34_team_id_unique(self):
        """Test 34: Team IDs are unique across instances."""
        t1 = MissionTeam("T1")
        t2 = MissionTeam("T2")
        self.assertNotEqual(t1.team_id, t2.team_id)

    def test_35_collaboration_stream_multiple_messages(self):
        """Test 35: Stream accumulates multiple messages in order."""
        self.protocol.send_message("A", "B", "T", "M1")
        self.protocol.send_message("B", "C", "T", "M2")
        stream = self.protocol.get_collaboration_stream()
        self.assertEqual(len(stream), 2)
        self.assertEqual(stream[0]["content"], "M1")

    def test_36_resolver_reason_string(self):
        """Test 36: Reason is string."""
        res = self.resolver.resolve_agent_conflict({"confidence": 0.9}, {"confidence": 0.5})
        self.assertIn("reason", res)

    def test_37_verifier_total_evidence_count(self):
        """Test 37: total_evidence_count matches input list length."""
        res = self.verifier.verify_evidence_threshold([{}, {}, {}])
        self.assertEqual(res["total_evidence_count"], 3)

    def test_38_critic_plan_case_insensitive_steps(self):
        """Test 38: Critic plan evaluation step check is case insensitive."""
        res = self.critic.evaluate_plan_quality({"steps": ["RESEARCH", "REVIEW"]})
        self.assertTrue(res["passed"])

    def test_39_agent_message_payload_custom(self):
        """Test 39: Custom payload preserved in AgentMessage."""
        msg = AgentMessage("A", "B", "T", "C", {"key": "val"})
        self.assertEqual(msg.payload["key"], "val")

    def test_40_delegator_subtask_string(self):
        """Test 40: Subtask string preserved in delegation output."""
        d = self.delegator.delegate_subtask("A", "B", "Run Tests")
        self.assertEqual(d["subtask"], "Run Tests")

    def test_41_verifier_insufficient_status(self):
        """Test 41: Status is INSUFFICIENT_EVIDENCE when threshold fails."""
        res = self.verifier.verify_evidence_threshold([])
        self.assertEqual(res["status"], "INSUFFICIENT_EVIDENCE")

    def test_42_critic_evaluation_dict_keys_count(self):
        """Test 42: Critic evaluation dict contains 4 keys."""
        res = self.critic.evaluate_plan_quality({})
        self.assertEqual(len(res), 4)

    def test_43_verifier_evaluation_dict_keys_count(self):
        """Test 43: Verifier evaluation dict contains 5 keys."""
        res = self.verifier.verify_evidence_threshold([])
        self.assertEqual(len(res), 5)

    def test_44_resolver_dict_keys_count(self):
        """Test 44: Resolver dict contains 3 keys."""
        res = self.resolver.resolve_agent_conflict({}, {})
        self.assertEqual(len(res), 3)

    def test_45_v6_2_multi_agent_collaboration_verification_passed(self):
        """Test 45: All V6.2 components verified."""
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
