from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class ContextPackage:
    task: str
    user_request: str
    memory: List[Dict[str, Any]] = field(default_factory=list)
    knowledge: List[Dict[str, Any]] = field(default_factory=list)
    emails: List[Dict[str, Any]] = field(default_factory=list)
    calendar: List[Dict[str, Any]] = field(default_factory=list)
    tasks: List[Dict[str, Any]] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)
    trace: Dict[str, Any] = field(default_factory=dict)

    def to_prompt_context(self) -> str:
        """Formats context in strict Source Priority Order:
        1. User Instruction
        2. Live Data (Emails / Calendar / Tasks)
        3. Personal Memory
        4. Knowledge RAG
        """
        sections = []
        
        # 1. User Instruction
        sections.append(f"### USER INSTRUCTION\n{self.user_request}")
        
        # 2. Live Data
        if self.emails:
            email_lines = []
            for e in self.emails:
                email_lines.append(f"- [{e.get('priority', 'normal').upper()}] Sender: {e.get('sender')} | Subject: {e.get('subject')} | Action: {e.get('suggested_action', 'None')}")
            sections.append("### LIVE RECENT EMAILS\n" + "\n".join(email_lines))
            
        if self.calendar:
            cal_lines = [f"- {c}" for c in self.calendar]
            sections.append("### TODAY'S CALENDAR\n" + "\n".join(cal_lines))
            
        if self.tasks:
            task_lines = [f"- {t}" for t in self.tasks]
            sections.append("### ACTIVE TASKS\n" + "\n".join(task_lines))
            
        # 3. Personal Memory
        if self.memory:
            mem_lines = []
            for m in self.memory:
                mem_lines.append(f"- [{m.get('type', 'fact').upper()}] {m.get('content')} (Source: {m.get('source')})")
            sections.append("### PERSONAL MEMORY & PREFERENCES\n" + "\n".join(mem_lines))
            
        # 4. Knowledge RAG
        if self.knowledge:
            rag_lines = []
            for k in self.knowledge:
                fn = k.get('metadata', {}).get('filename', 'doc')
                cat = k.get('metadata', {}).get('category', 'knowledge')
                rag_lines.append(f"[{cat}/{fn}]: {k.get('text')}")
            sections.append("### RETRIEVED KNOWLEDGE (RAG)\n" + "\n\n".join(rag_lines))
            
        return "\n\n".join(sections)
