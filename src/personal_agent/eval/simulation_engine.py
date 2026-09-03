import time
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional

@dataclass
class SyntheticWorld:
    world_id: str
    name: str
    emails_count: int = 10
    calendar_events_count: int = 3
    tasks_count: int = 5
    goals_count: int = 2
    deadlines_count: int = 1
    is_network_available: bool = True
    has_email_storm: bool = False
    has_prompt_injection: bool = False
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class SimulationEngine:
    def create_synthetic_world(
        self,
        name: str = "Normal Day Scenario",
        emails_count: int = 10,
        calendar_events_count: int = 3,
        tasks_count: int = 5,
        goals_count: int = 5,
        deadlines_count: int = 1,
        is_network_available: bool = True,
        has_email_storm: bool = False,
        has_prompt_injection: bool = False
    ) -> SyntheticWorld:
        return SyntheticWorld(
            world_id=f"world_{int(time.time()*1000)}",
            name=name,
            emails_count=emails_count,
            calendar_events_count=calendar_events_count,
            tasks_count=tasks_count,
            goals_count=goals_count,
            deadlines_count=deadlines_count,
            is_network_available=is_network_available,
            has_email_storm=has_email_storm,
            has_prompt_injection=has_prompt_injection
        )

    def create_deadline_crisis_world(self) -> SyntheticWorld:
        return self.create_synthetic_world(
            name="University Deadline Crisis",
            emails_count=25,
            calendar_events_count=6,
            tasks_count=12,
            goals_count=4,
            deadlines_count=3
        )

    def create_email_storm_world(self) -> SyntheticWorld:
        return self.create_synthetic_world(
            name="Email Storm Scenario",
            emails_count=100,
            has_email_storm=True
        )

    def create_adversarial_world(self) -> SyntheticWorld:
        return self.create_synthetic_world(
            name="Adversarial Prompt Injection Scenario",
            has_prompt_injection=True
        )
