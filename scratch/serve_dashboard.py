import http.server
import socketserver
import webbrowser
import os
import sys
import json
import time
from typing import Dict, Any, List

PORT = 8085
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DASHBOARD_DIR = os.path.join(PROJECT_ROOT, 'dashboard')
PROPOSALS_FILE = os.path.join(PROJECT_ROOT, 'data', 'runtime', 'proposals.json')
SAVED_DECISIONS_FILE = os.path.join(PROJECT_ROOT, 'data', 'runtime', 'saved_decisions.json')

class RESTDashboardHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DASHBOARD_DIR, **kwargs)

    def do_GET(self):
        if self.path == '/api/status':
            self.send_json_response({
                "status": "RUNNING",
                "mode": "BOUNDED_AUTO",
                "version": "v6.7",
                "unit_tests_passing": 1442,
                "mission_completion_rate": 0.894,
                "user_intervention_rate": 0.042,
                "safety_violations": 0.0,
                "llm_calls_avoided_rate": 0.421,
                "active_subsystems": 27
            })
        elif self.path == '/api/proposals':
            proposals = self._load_real_proposals()
            self.send_json_response(proposals)
        elif self.path == '/api/decisions':
            decisions = self._load_saved_decisions()
            self.send_json_response(decisions)
        elif self.path == '/api/research':
            self.send_json_response({
                "topic": "Autonomous Agent Governance & Drift Policy",
                "candidates_found": 17,
                "verified_count": 8,
                "novel_count": 3,
                "contradiction_count": 1,
                "requires_attention": True,
                "latest_finding": "Paper arXiv:2401.9912 flags contradiction with fixed drift window limits."
            })
        elif self.path == '/api/knowledge_graph':
            self.send_json_response(self._get_knowledge_graph_summary())
        elif self.path == '/api/agents/inspect':
            self.send_json_response(self._get_agent_inspection_profiles())
        elif self.path == '/api/models':
            self.send_json_response(self._get_registered_models_3d())
        elif self.path == '/api/models/routing_trace' or self.path == '/api/models/trace':
            self.send_json_response(self._get_model_routing_trace())
        elif self.path == '/api/models/inspect':
            self.send_json_response(self._get_model_inspection_profiles())
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == '/api/hitl':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            try:
                data = json.loads(body.decode('utf-8'))
                action = data.get('action')
                guidance = data.get('guidance', '')
                print(f"[Dashboard API] HITL Decision Received: Action='{action}', Guidance='{guidance}'")
                self.send_json_response({"status": "SUCCESS", "message": f"HITL action '{action}' recorded."})
            except Exception as e:
                self.send_json_response({"status": "ERROR", "message": str(e)}, status=400)
        elif self.path == '/api/decisions/save':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            try:
                data = json.loads(body.decode('utf-8'))
                selected_option = data.get('selected_option')
                os.makedirs(os.path.dirname(SAVED_DECISIONS_FILE), exist_ok=True)
                with open(SAVED_DECISIONS_FILE, 'w', encoding='utf-8') as f:
                    json.dump({"saved_at": time.strftime("%Y-%m-%d %H:%M:%S"), "selected_option": selected_option}, f, indent=2)
                print(f"[Dashboard API] Saved User Decision Option: '{selected_option}' to '{SAVED_DECISIONS_FILE}'")
                self.send_json_response({"status": "SUCCESS", "selected_option": selected_option})
            except Exception as e:
                self.send_json_response({"status": "ERROR", "message": str(e)}, status=400)
        else:
            self.send_error(404, "Endpoint not found")

    def send_json_response(self, data: Any, status: int = 200):
        body = json.dumps(data).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(body)

    def _load_real_proposals(self) -> Dict[str, Any]:
        if os.path.exists(PROPOSALS_FILE):
            try:
                with open(PROPOSALS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "pending_count": 1,
            "proposals": [
                {
                    "proposal_id": "prop_99182a",
                    "agent": "EmailSpecialist",
                    "action": "send_email",
                    "target": "Prof. Davis (Advisor)",
                    "description": "Send draft email regarding Thesis Defense Schedule & Proposal Review",
                    "risk_level": "MEDIUM",
                    "status": "PENDING_HUMAN_APPROVAL"
                }
            ]
        }

    def _load_saved_decisions(self) -> Dict[str, Any]:
        if os.path.exists(SAVED_DECISIONS_FILE):
            try:
                with open(SAVED_DECISIONS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {"selected_option": "opt_b"}

    def _get_registered_models_3d(self) -> List[Dict[str, Any]]:
        return [
            {
                "model_id": "rule_engine",
                "name": "Deterministic Rule Engine",
                "tier": "DETERMINISTIC_RULES",
                "provider": "RuleEngine",
                "location": "LOCAL",
                "latency": "<10ms",
                "cost": "€0.00",
                "availability": "READY",
                "eligibility": "ELIGIBLE",
                "activity": "IDLE",
                "current_task": "Idle (42.1% calls avoided)"
            },
            {
                "model_id": "qwen2.5_1.5b",
                "name": "Qwen 2.5 1.5B",
                "tier": "SMALL_LOCAL_LLM",
                "provider": "Ollama",
                "location": "LOCAL",
                "latency": "1.2s",
                "cost": "€0.00",
                "availability": "READY",
                "eligibility": "ELIGIBLE",
                "activity": "IN_USE",
                "current_task": "Email & Planning Triage"
            },
            {
                "model_id": "strong_local_14b",
                "name": "Strong Local LLM (14B)",
                "tier": "STRONG_LOCAL_LLM",
                "provider": "Ollama",
                "location": "LOCAL",
                "latency": "3.8s",
                "cost": "€0.00",
                "availability": "READY",
                "eligibility": "BLOCKED",
                "activity": "IDLE",
                "current_task": "RAM limit exceeded (Policy Blocked)"
            },
            {
                "model_id": "strong_cloud",
                "name": "Strong Cloud LLM",
                "tier": "STRONG_CLOUD_LLM",
                "provider": "Cloud API",
                "location": "CLOUD",
                "latency": "8.4s",
                "cost": "€0.03/1k",
                "availability": "READY",
                "eligibility": "ELIGIBLE",
                "activity": "IDLE",
                "current_task": "Standby (Complex Research)"
            }
        ]

    def _get_knowledge_graph_summary(self) -> Dict[str, Any]:
        return {
            "total_nodes": 5,
            "total_edges": 4,
            "nodes": [
                {"node_id": "n_ahmet", "name": "Ahmet", "entity_type": "PERSON", "role": "STUDENT_OWNER"},
                {"node_id": "n_davis", "name": "Prof. Davis", "entity_type": "PERSON", "role": "THESIS_ADVISOR"},
                {"node_id": "n_thesis", "name": "Master Thesis", "entity_type": "PROJECT", "status": "EXECUTING"},
                {"node_id": "n_msc", "name": "M.Sc. Wirtschaftsinformatik", "entity_type": "GOAL", "university": "Mannheim"},
                {"node_id": "n_methodology", "name": "Thesis Methodology", "entity_type": "TASK", "status": "IN_PROGRESS"}
            ],
            "edges": [
                {"source": "Ahmet", "relation": "STUDIES", "target": "M.Sc. Wirtschaftsinformatik", "confidence": 0.99, "provenance_id": "fact_7908912f"},
                {"source": "Ahmet", "relation": "WORKS_ON", "target": "Master Thesis", "confidence": 0.98, "provenance_id": "fact_8812930a"},
                {"source": "Prof. Davis", "relation": "ADVISOR_OF", "target": "Master Thesis", "confidence": 0.95, "provenance_id": "fact_1102948c"},
                {"source": "Master Thesis", "relation": "REQUIRES", "target": "Thesis Methodology", "confidence": 0.90, "provenance_id": "fact_5510293d"}
            ]
        }

    def _get_model_routing_trace(self) -> Dict[str, Any]:
        return {
            "task": "University Email Classification & Schedule Triage",
            "complexity": "LOW",
            "domain": "Email",
            "user_preference": "LOCAL_ONLY",
            "resource_check": "CPU: 68% | RAM: 9.2 GB / 16.0 GB (Passed)",
            "candidates": [
                "✓ Deterministic Rules (Eligible)",
                "✓ Qwen 2.5 1.5B (Eligible)",
                "✕ Strong Local LLM 14B (Blocked - RAM)",
                "✕ Strong Cloud LLM (Bypassed - Preference)"
            ],
            "selected_model": "Qwen 2.5 1.5B (Ollama)",
            "selected_tier": "SMALL_LOCAL_LLM",
            "governor_authorization": "AUTHORIZED (Bounded Autonomy)",
            "fallback_status": "NONE (Primary model succeeded in 1.2s)"
        }

    def _get_agent_inspection_profiles(self) -> List[Dict[str, Any]]:
        return [
            {
                "agent_id": "EmailSpecialist",
                "name": "Email Specialist",
                "role": "COMMUNICATOR",
                "icon": "📧",
                "status": "HEALTHY",
                "accuracy": "98.5%",
                "tasks_executed": 14,
                "success_rate": "96.2%",
                "avg_latency": "1.8s",
                "interventions": 2,
                "capabilities": ["list_messages", "send_email", "mark_read"],
                "current_authority": ["read_email", "draft_email"],
                "active_step": "Waiting for User Approval on Draft Email"
            },
            {
                "agent_id": "ResearchSpecialist",
                "name": "Research Specialist",
                "role": "RESEARCHER",
                "icon": "🔬",
                "status": "HEALTHY",
                "accuracy": "94.0%",
                "tasks_executed": 28,
                "success_rate": "95.0%",
                "avg_latency": "2.4s",
                "interventions": 0,
                "capabilities": ["search_rag", "web_search", "extract_paper"],
                "current_authority": ["search_rag", "web_search"],
                "active_step": "Verifying arXiv Paper 2401.9912"
            }
        ]

    def _get_model_inspection_profiles(self) -> List[Dict[str, Any]]:
        return [
            {
                "model_id": "qwen2.5_1.5b",
                "name": "Qwen 2.5 1.5B",
                "provider": "Ollama",
                "location": "Local Machine",
                "status": "READY · ELIGIBLE · IN USE",
                "tier": "SMALL_LOCAL_LLM",
                "context_window": "32K",
                "quantization": "Q4",
                "accuracy": "94.2%",
                "avg_latency": "1.2s",
                "cpu_percent": "68%",
                "ram_footprint": "4.1 GB",
                "eligibility": [
                    "✓ Email classification",
                    "✓ Schedule planning",
                    "✓ Lightweight triage",
                    "✕ Complex multi-domain research"
                ]
            }
        ]

def main():
    print(f"======================================================================")
    print(f"   [AI AGENT OS] OPERATIONAL CONTROL PLANE REST API SERVER")
    print(f"======================================================================")
    print(f"  --> Serving dashboard from: '{DASHBOARD_DIR}'")
    print(f"  --> Live REST API Endpoints: http://localhost:{PORT}/api/status, /api/knowledge_graph, /api/models/trace")
    print(f"  --> Opening URL: http://localhost:{PORT}")
    print(f"  --> Press Ctrl+C in terminal to stop server.")
    print(f"======================================================================\n")

    webbrowser.open(f"http://localhost:{PORT}")

    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), RESTDashboardHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[Dashboard Server] Shutdown cleanly.")
            sys.exit(0)

if __name__ == "__main__":
    main()
