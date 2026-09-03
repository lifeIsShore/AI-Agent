from typing import Dict, Any, Optional
from personal_agent.learning.mission_outcome_analyzer import MissionOutcomeAnalyzer
from personal_agent.learning.strategy_extractor import StrategyExtractor
from personal_agent.learning.mission_strategy_store import MissionStrategyStore
from personal_agent.learning.strategy_selector import StrategySelector

class MissionLearningEngine:
    def __init__(self):
        self.analyzer = MissionOutcomeAnalyzer()
        self.extractor = StrategyExtractor()
        self.store = MissionStrategyStore()
        self.selector = StrategySelector()

    def process_completed_mission(self, mission_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyzes outcome, extracts strategy if successful, and saves to strategy store."""
        analysis = self.analyzer.analyze_mission_outcome(mission_data)
        extracted = None

        if analysis.get("success_rate", 0.0) >= 0.70:
            extracted = self.extractor.extract_strategy(mission_data, analysis)
            self.store.save_strategy(extracted)

        return {
            "analysis": analysis,
            "extracted_strategy": extracted,
            "status": "PROCESSED"
        }

    def recommend_mission_strategy(self, domain: str) -> Optional[Dict[str, Any]]:
        return self.selector.select_best_strategy(domain, self.store)
