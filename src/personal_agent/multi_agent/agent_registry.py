from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional
from personal_agent.autonomy.autonomy_policy import LEVEL_2_APPROVAL, LEVEL_3_BOUNDED_AUTO, LEVEL_4_SUPERVISED_AUTO

@dataclass
class AgentSpecialistProfile:
    agent_id: str
    role: str
    description: str
    capabilities: List[str] = field(default_factory=list)
    allowed_tools: List[str] = field(default_factory=list)
    maximum_autonomy_level: str = LEVEL_3_BOUNDED_AUTO
    context_requirements: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class AgentRegistry:
    def __init__(self):
        self.profiles: Dict[str, AgentSpecialistProfile] = {}
        self._register_default_specialists()

    def _register_default_specialists(self):
        # 1. Email Specialist
        self.register_agent(AgentSpecialistProfile(
            agent_id="EmailSpecialist",
            role="Email Triage & Draft Specialist",
            description="Manages inbox, email search, labeling, and drafting responses.",
            capabilities=["gmail.read", "gmail.label", "gmail.draft"],
            allowed_tools=["list_messages", "get_message", "mark_read", "create_draft"],
            maximum_autonomy_level=LEVEL_3_BOUNDED_AUTO
        ))

        # 2. Research Specialist
        self.register_agent(AgentSpecialistProfile(
            agent_id="ResearchSpecialist",
            role="Literature & RAG Research Specialist",
            description="Searches research databases, RAG knowledge bases, and summarizes documents.",
            capabilities=["rag.query", "system.read"],
            allowed_tools=["rag_search", "view_file", "search_web"],
            maximum_autonomy_level=LEVEL_3_BOUNDED_AUTO
        ))

        # 3. Calendar Specialist
        self.register_agent(AgentSpecialistProfile(
            agent_id="CalendarSpecialist",
            role="Calendar Scheduling Specialist",
            description="Schedules events, calculates free slots, and resolves scheduling conflicts.",
            capabilities=["calendar.read", "calendar.write"],
            allowed_tools=["list_events", "create_calendar_event", "reschedule_event"],
            maximum_autonomy_level=LEVEL_3_BOUNDED_AUTO
        ))

        # 4. Browser Specialist
        self.register_agent(AgentSpecialistProfile(
            agent_id="BrowserSpecialist",
            role="DOM & Vision Web Browser Specialist",
            description="Navigates web pages, extracts compact DOM summaries, and executes web actions.",
            capabilities=["browser.navigate", "browser.interact"],
            allowed_tools=["browser_navigate", "browser_click", "browser_type", "browser_download"],
            maximum_autonomy_level=LEVEL_2_APPROVAL
        ))

        # 5. Planning Specialist
        self.register_agent(AgentSpecialistProfile(
            agent_id="PlanningSpecialist",
            role="Goal & Milestone Planning Specialist",
            description="Decomposes long-horizon goals into DAG milestones and manages resource allocation.",
            capabilities=["planning.decompose", "goals.arbitrate"],
            allowed_tools=["create_task", "arbitrate_goals", "generate_dag"],
            maximum_autonomy_level=LEVEL_3_BOUNDED_AUTO
        ))

        # 6. Document Specialist
        self.register_agent(AgentSpecialistProfile(
            agent_id="DocumentSpecialist",
            role="Document Summarization & Writing Specialist",
            description="Drafts, edits, and verifies local document files.",
            capabilities=["system.read", "system.write"],
            allowed_tools=["view_file", "write_to_file", "replace_file_content"],
            maximum_autonomy_level=LEVEL_3_BOUNDED_AUTO
        ))

    def register_agent(self, profile: AgentSpecialistProfile) -> AgentSpecialistProfile:
        self.profiles[profile.agent_id] = profile
        return profile

    def get_agent(self, agent_id: str) -> Optional[AgentSpecialistProfile]:
        return self.profiles.get(agent_id)

    def get_all_agents(self) -> List[AgentSpecialistProfile]:
        return list(self.profiles.values())

    def get_agents_by_capability(self, capability: str) -> List[AgentSpecialistProfile]:
        return [p for p in self.profiles.values() if capability in p.capabilities]
