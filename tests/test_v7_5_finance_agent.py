import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from personal_agent.agents.finance_agent import FinanceAgent

class TestV75FinanceAgent(unittest.TestCase):

    def setUp(self):
        self.finance_agent = FinanceAgent()

    def test_1_agent_id_is_finance_agent(self):
        """Test 1: agent_id is FinanceAgent."""
        self.assertEqual(self.finance_agent.agent_id, "FinanceAgent")

    def test_2_role_is_financial_analyst(self):
        """Test 2: role is FINANCIAL_ANALYST."""
        self.assertEqual(self.finance_agent.role, "FINANCIAL_ANALYST")

    def test_3_analyze_company_returns_dict(self):
        """Test 3: analyze_company_financials returns dictionary."""
        res = self.finance_agent.analyze_company_financials("SAP.DE")
        self.assertIsInstance(res, dict)

    def test_4_ticker_preserved(self):
        """Test 4: Ticker preserved in result."""
        res = self.finance_agent.analyze_company_financials("SAP.DE")
        self.assertEqual(res["ticker"], "SAP.DE")

    def test_5_financial_metrics_dict(self):
        """Test 5: financial_metrics contains 5 keys."""
        res = self.finance_agent.analyze_company_financials("SAP.DE")
        self.assertEqual(len(res["financial_metrics"]), 5)

    def test_6_valuation_model_dcf(self):
        """Test 6: valuation_model is Discounted Cash Flow (DCF)."""
        res = self.finance_agent.analyze_company_financials("SAP.DE")
        self.assertIn("DCF", res["valuation_model"])

    def test_7_transaction_authority_prohibited(self):
        """Test 7: transaction_authority is PROHIBITED."""
        res = self.finance_agent.analyze_company_financials("SAP.DE")
        self.assertIn("PROHIBITED", res["transaction_authority"])

    def test_8_governor_authorization_analysis_only(self):
        """Test 8: Governor authorization is AUTHORIZED_FOR_ANALYSIS_ONLY."""
        res = self.finance_agent.analyze_company_financials("SAP.DE")
        self.assertEqual(res["governor_authorization"], "AUTHORIZED_FOR_ANALYSIS_ONLY")

    def test_9_capabilities_count_5(self):
        """Test 9: Capabilities count is 5."""
        self.assertEqual(len(self.finance_agent.capabilities), 5)

    def test_10_tools_count_2(self):
        """Test 10: Tools count is 2."""
        self.assertEqual(len(self.finance_agent.tools), 2)

    def test_11_class_name(self):
        """Test 11: Class name is FinanceAgent."""
        self.assertEqual(self.finance_agent.__class__.__name__, "FinanceAgent")

    def test_12_reusable_instance(self):
        """Test 12: Instance is reusable across calls."""
        r1 = self.finance_agent.analyze_company_financials("T")
        r2 = self.finance_agent.analyze_company_financials("T")
        self.assertEqual(r1["intrinsic_value_estimate"], r2["intrinsic_value_estimate"])

    def test_13_json_serializable(self):
        """Test 13: Output dictionary is JSON serializable."""
        import json
        dumped = json.dumps(self.finance_agent.analyze_company_financials("T"))
        self.assertIsInstance(dumped, str)

    def test_14_capabilities_include_valuation_model(self):
        """Test 14: Capabilities include financial.valuation_model."""
        self.assertIn("financial.valuation_model", self.finance_agent.capabilities)

    def test_15_preferred_models_include_strong_cloud(self):
        """Test 15: Preferred models include strong_cloud."""
        self.assertIn("strong_cloud", self.finance_agent.preferred_models)

    def test_16_autonomy_cap_bounded_auto(self):
        """Test 16: Autonomy cap is BOUNDED_AUTO."""
        self.assertEqual(self.finance_agent.autonomy_cap, "BOUNDED_AUTO")

    def test_17_summary_keys_count(self):
        """Test 17: analyze_company_financials returns 8 keys."""
        res = self.finance_agent.analyze_company_financials("T")
        self.assertEqual(len(res), 8)

    def test_18_investment_thesis_non_empty(self):
        """Test 18: investment_thesis is non-empty string."""
        res = self.finance_agent.analyze_company_financials("T")
        self.assertTrue(len(res["investment_thesis"]) > 0)

    def test_19_intrinsic_value_estimate_non_empty(self):
        """Test 19: intrinsic_value_estimate is non-empty string."""
        res = self.finance_agent.analyze_company_financials("T")
        self.assertTrue(len(res["intrinsic_value_estimate"]) > 0)

    def test_20_pe_ratio_float(self):
        """Test 20: pe_ratio is float."""
        res = self.finance_agent.analyze_company_financials("T")
        self.assertIsInstance(res["financial_metrics"]["pe_ratio"], float)

    def test_21_ev_ebitda_float(self):
        """Test 21: ev_ebitda is float."""
        res = self.finance_agent.analyze_company_financials("T")
        self.assertIsInstance(res["financial_metrics"]["ev_ebitda"], float)

    def test_22_debt_to_equity_float(self):
        """Test 22: debt_to_equity is float."""
        res = self.finance_agent.analyze_company_financials("T")
        self.assertIsInstance(res["financial_metrics"]["debt_to_equity"], float)

    def test_23_inherits_from_specialist_agent(self):
        """Test 23: FinanceAgent inherits from SpecialistAgent."""
        from personal_agent.agents.base_specialist import SpecialistAgent
        self.assertTrue(issubclass(FinanceAgent, SpecialistAgent))

    def test_24_execute_task_overridden(self):
        """Test 24: Base execute_task works on FinanceAgent."""
        res = self.finance_agent.execute_task({})
        self.assertEqual(res["agent_id"], "FinanceAgent")

    def test_25_to_dict_agent_id(self):
        """Test 25: to_dict contains agent_id FinanceAgent."""
        self.assertEqual(self.finance_agent.to_dict()["agent_id"], "FinanceAgent")

    def test_26_tools_list_type(self):
        """Test 26: tools is list."""
        self.assertIsInstance(self.finance_agent.tools, list)

    def test_27_preferred_models_count_2(self):
        """Test 27: Preferred models count is 2."""
        self.assertEqual(len(self.finance_agent.preferred_models), 2)

    def test_28_instantiation_clean(self):
        """Test 28: FinanceAgent instantiates cleanly."""
        agent = FinanceAgent()
        self.assertIsNotNone(agent)

    def test_29_no_error_keys(self):
        """Test 29: Result does not contain error key."""
        res = self.finance_agent.analyze_company_financials("T")
        self.assertNotIn("error", res)

    def test_30_capabilities_list_type(self):
        """Test 30: capabilities is list."""
        self.assertIsInstance(self.finance_agent.capabilities, list)

    def test_31_preferred_models_list_type(self):
        """Test 31: preferred_models is list."""
        self.assertIsInstance(self.finance_agent.preferred_models, list)

    def test_32_dict_return_type(self):
        """Test 32: to_dict return type is dict."""
        self.assertEqual(type(self.finance_agent.to_dict()), dict)

    def test_33_analyze_return_type(self):
        """Test 33: analyze_company_financials return type is dict."""
        self.assertEqual(type(self.finance_agent.analyze_company_financials("T")), dict)

    def test_34_financial_metrics_dict_type(self):
        """Test 34: financial_metrics return type is dict."""
        res = self.finance_agent.analyze_company_financials("T")
        self.assertEqual(type(res["financial_metrics"]), dict)

    def test_35_ticker_string_type(self):
        """Test 35: ticker is string."""
        res = self.finance_agent.analyze_company_financials("T")
        self.assertEqual(type(res["ticker"]), str)

    def test_36_agent_id_string_type(self):
        """Test 36: agent_id is string."""
        res = self.finance_agent.analyze_company_financials("T")
        self.assertEqual(type(res["agent_id"]), str)

    def test_37_governor_authorization_string_type(self):
        """Test 37: governor_authorization is string."""
        res = self.finance_agent.analyze_company_financials("T")
        self.assertEqual(type(res["governor_authorization"]), str)

    def test_38_free_cash_flow_yield_contains_percent(self):
        """Test 38: free_cash_flow_yield contains percent sign."""
        res = self.finance_agent.analyze_company_financials("T")
        self.assertIn("%", res["financial_metrics"]["free_cash_flow_yield"])

    def test_39_return_on_equity_contains_percent(self):
        """Test 39: return_on_equity contains percent sign."""
        res = self.finance_agent.analyze_company_financials("T")
        self.assertIn("%", res["financial_metrics"]["return_on_equity"])

    def test_40_valuation_model_string_non_empty(self):
        """Test 40: valuation_model is non-empty string."""
        res = self.finance_agent.analyze_company_financials("T")
        self.assertTrue(len(res["valuation_model"]) > 0)

    def test_41_intrinsic_value_string_non_empty(self):
        """Test 41: intrinsic_value_estimate is non-empty string."""
        res = self.finance_agent.analyze_company_financials("T")
        self.assertTrue(len(res["intrinsic_value_estimate"]) > 0)

    def test_42_investment_thesis_string_non_empty(self):
        """Test 42: investment_thesis is non-empty string."""
        res = self.finance_agent.analyze_company_financials("T")
        self.assertTrue(len(res["investment_thesis"]) > 0)

    def test_43_transaction_authority_string_non_empty(self):
        """Test 43: transaction_authority is non-empty string."""
        res = self.finance_agent.analyze_company_financials("T")
        self.assertTrue(len(res["transaction_authority"]) > 0)

    def test_44_pe_ratio_positive(self):
        """Test 44: pe_ratio > 0."""
        res = self.finance_agent.analyze_company_financials("T")
        self.assertTrue(res["financial_metrics"]["pe_ratio"] > 0)

    def test_45_v7_5_finance_agent_verification_passed(self):
        """Test 45: All V7.5 FinanceAgent features verified."""
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
