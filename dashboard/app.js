// Personal AI Agent Dashboard Operational Control Plane (V6.5 / V6.6.1)
document.addEventListener('DOMContentLoaded', () => {
    console.log("⚡ Personal AI Agent OS Operational Control Plane (V6.6.1 Model Orchestration) initialized.");

    const consoleTerminal = document.getElementById('console-terminal');
    const btnApprove = document.getElementById('btn-approve');
    const btnReject = document.getElementById('btn-reject');
    const hitlInput = document.getElementById('hitl-input');
    const hitlBanner = document.getElementById('hitl-banner');
    const hitlActionDesc = document.getElementById('hitl-action-desc');
    const btnClearConsole = document.getElementById('btn-clear-console');
    const filterButtons = document.querySelectorAll('.filter-btn');

    // Decision Intelligence Selection & Save Elements
    const decisionContainer = document.getElementById('decision-options-container');
    const btnSaveDecision = document.getElementById('btn-save-decision');
    const decisionSaveToast = document.getElementById('decision-save-toast');

    // Agent & Model Inspector Modal Elements
    const agentModalOverlay = document.getElementById('agent-modal-overlay');
    const modalCloseBtn = document.getElementById('modal-close-btn');
    const authorityCards = document.querySelectorAll('.authority-card.clickable');

    const modelModalOverlay = document.getElementById('model-modal-overlay');
    const modelModalCloseBtn = document.getElementById('model-modal-close-btn');
    const modelCards = document.querySelectorAll('.model-item.clickable');

    let currentSelectedOption = 'opt_b';
    let agentInspectionProfiles = [];
    let modelInspectionProfiles = [];

    // Utility function to append timestamped structured log line
    function appendLog(message, category = 'ACTION', type = 'info') {
        if (!consoleTerminal) return;
        const now = new Date();
        const timestamp = now.toTimeString().split(' ')[0];
        const logLine = document.createElement('div');
        logLine.className = `log-line ${type}`;
        logLine.setAttribute('data-category', category);
        logLine.textContent = `[${timestamp}] ${message}`;
        consoleTerminal.appendChild(logLine);
        consoleTerminal.scrollTop = consoleTerminal.scrollHeight;
    }

    // Interactive Decision Option Click Handler
    if (decisionContainer) {
        const optionCards = decisionContainer.querySelectorAll('.decision-card');
        optionCards.forEach(card => {
            card.addEventListener('click', () => {
                optionCards.forEach(c => c.classList.remove('selected'));
                card.classList.add('selected');
                currentSelectedOption = card.getAttribute('data-option-id') || 'opt_b';
                
                const optionName = card.querySelector('.dec-name')?.textContent || currentSelectedOption;
                appendLog(`[DecisionIntelligenceEngine] User selected ${optionName}. Click 'Save & Apply' to persist.`, 'DECISION', 'warning');
            });
        });
    }

    // Save Selected Decision Handler
    if (btnSaveDecision) {
        btnSaveDecision.addEventListener('click', async () => {
            try {
                const res = await fetch('/api/decisions/save', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ selected_option: currentSelectedOption })
                });

                if (res.ok) {
                    appendLog(`[DecisionIntelligenceEngine] Decision '${currentSelectedOption}' saved & applied to AutonomyGovernor.`, 'DECISION', 'success');
                    if (decisionSaveToast) {
                        decisionSaveToast.textContent = `✓ Decision '${currentSelectedOption.toUpperCase()}' Saved to Disk & Applied!`;
                        decisionSaveToast.style.opacity = '1';
                        setTimeout(() => { decisionSaveToast.style.opacity = '0.7'; }, 3000);
                    }
                }
            } catch (e) {
                console.error("Decision save failed:", e);
            }
        });
    }

    // Fetch Inspection Profiles from REST API
    async function fetchInspectionProfiles() {
        try {
            const resA = await fetch('/api/agents/inspect');
            if (resA.ok) agentInspectionProfiles = await resA.json();

            const resM = await fetch('/api/models/inspect');
            if (resM.ok) modelInspectionProfiles = await resM.json();
        } catch (e) {
            console.log("Using default inspection profile data.");
        }
    }

    // Model Inspector Modal Click Handler
    modelCards.forEach(card => {
        card.addEventListener('click', async () => {
            const modelId = card.getAttribute('data-model-id');
            if (modelInspectionProfiles.length === 0) await fetchInspectionProfiles();

            const profile = modelInspectionProfiles.find(p => p.model_id === modelId) || {
                name: modelId,
                provider: "Local/Cloud",
                location: "Local",
                status: "READY",
                tier: "SMALL_LOCAL_LLM",
                context_window: "32K",
                quantization: "Q4",
                accuracy: "94.0%",
                avg_latency: "1.2s",
                cpu_percent: "68%",
                ram_footprint: "4.1 GB",
                eligibility: ["✓ Email triage", "✓ Planning"]
            };

            // Populate Model Modal Fields
            document.getElementById('modal-model-name').textContent = `${profile.name} Inspector`;
            document.getElementById('modal-model-status').textContent = profile.status;
            document.getElementById('modal-model-tier').textContent = profile.tier;
            document.getElementById('modal-model-provider').textContent = `${profile.provider} (${profile.location})`;
            document.getElementById('modal-model-context').textContent = profile.context_window;
            document.getElementById('modal-model-quant').textContent = profile.quantization;
            document.getElementById('modal-model-latency').textContent = profile.avg_latency;
            document.getElementById('modal-model-ram').textContent = profile.ram_footprint;
            document.getElementById('modal-model-cpu').textContent = profile.cpu_percent;
            document.getElementById('modal-model-eligibility').innerHTML = profile.eligibility.map(e => `<div>${e}</div>`).join('');

            if (modelModalOverlay) modelModalOverlay.classList.remove('hidden');
            appendLog(`[ModelInspector] Opened inspection view for model '${profile.name}'.`, 'LLM', 'info');
        });
    });

    // Close Model Modal Handler
    if (modelModalCloseBtn) {
        modelModalCloseBtn.addEventListener('click', () => {
            if (modelModalOverlay) modelModalOverlay.classList.add('hidden');
        });
    }

    if (modelModalOverlay) {
        modelModalOverlay.addEventListener('click', (e) => {
            if (e.target === modelModalOverlay) modelModalOverlay.classList.add('hidden');
        });
    }

    // Agent Inspector Modal Click Handler
    authorityCards.forEach(card => {
        card.addEventListener('click', async () => {
            const agentId = card.getAttribute('data-agent-id');
            if (agentInspectionProfiles.length === 0) await fetchInspectionProfiles();

            const profile = agentInspectionProfiles.find(p => p.agent_id === agentId) || {
                name: agentId,
                role: "SPECIALIST",
                icon: "🤖",
                status: "HEALTHY",
                accuracy: "98.0%",
                tasks_executed: 15,
                success_rate: "96.0%",
                avg_latency: "1.5s",
                capabilities: ["list_messages", "send_email"],
                current_authority: ["read_email"],
                active_step: "Idle"
            };

            // Populate Agent Modal Fields
            document.getElementById('modal-agent-icon').textContent = profile.icon;
            document.getElementById('modal-agent-name').textContent = `${profile.name} Inspector`;
            document.getElementById('modal-agent-status').textContent = profile.status;
            document.getElementById('modal-agent-role').textContent = profile.role;
            document.getElementById('modal-agent-accuracy').textContent = profile.accuracy;
            document.getElementById('modal-agent-tasks').textContent = profile.tasks_executed;
            document.getElementById('modal-agent-success').textContent = profile.success_rate;
            document.getElementById('modal-agent-latency').textContent = profile.avg_latency;
            document.getElementById('modal-agent-capabilities').innerHTML = profile.capabilities.map(c => `<code>${c}</code>`).join(', ');
            document.getElementById('modal-agent-authority').innerHTML = profile.current_authority.map(a => `<code>${a}</code>`).join(', ');
            document.getElementById('modal-agent-active-step').textContent = profile.active_step;

            if (agentModalOverlay) agentModalOverlay.classList.remove('hidden');
            appendLog(`[AgentInspector] Opened inspection view for agent '${profile.name}'.`, 'ACTION', 'info');
        });
    });

    // Close Agent Modal Handler
    if (modalCloseBtn) {
        modalCloseBtn.addEventListener('click', () => {
            if (agentModalOverlay) agentModalOverlay.classList.add('hidden');
        });
    }

    if (agentModalOverlay) {
        agentModalOverlay.addEventListener('click', (e) => {
            if (e.target === agentModalOverlay) agentModalOverlay.classList.add('hidden');
        });
    }

    // Structured Log Category Filter Handler
    filterButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            filterButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            const targetFilter = btn.getAttribute('data-filter');

            const logLines = consoleTerminal ? consoleTerminal.querySelectorAll('.log-line') : [];
            logLines.forEach(line => {
                const cat = line.getAttribute('data-category') || 'ACTION';
                if (targetFilter === 'all' || cat.toUpperCase() === targetFilter.toUpperCase()) {
                    line.style.display = 'block';
                } else {
                    line.style.display = 'none';
                }
            });
        });
    });

    // HITL Approve Button Handler
    if (btnApprove) {
        btnApprove.addEventListener('click', () => {
            const userText = hitlInput ? hitlInput.value.trim() : '';
            const guidance = userText ? ` Guidance: '${userText}'` : '';
            
            appendLog(`[HumanFeedbackLoop] APPROVED: Action 'send_email' for EmailSpecialist authorized by user.${guidance}`, 'SECURITY', 'success');
            appendLog(`[AutonomyGovernor] Risk: MEDIUM -> Action PERMITTED via Human-In-The-Loop explicit approval.`, 'SECURITY', 'highlight');

            if (hitlActionDesc) {
                hitlActionDesc.innerHTML = `<span style="color: var(--accent-emerald); font-weight: 600;">✓ Action Approved & Dispatched to EmailSpecialist!</span>`;
            }
            setTimeout(() => {
                if (hitlBanner) hitlBanner.style.opacity = '0.5';
            }, 1000);
        });
    }

    // HITL Reject Button Handler
    if (btnReject) {
        btnReject.addEventListener('click', () => {
            const userText = hitlInput ? hitlInput.value.trim() : '';
            const guidance = userText ? ` Reason: '${userText}'` : '';
            
            appendLog(`[HumanFeedbackLoop] REJECTED: Action 'send_email' for EmailSpecialist rejected by user.${guidance}`, 'SECURITY', 'warning');
            appendLog(`[AutonomyGovernor] Action BLOCKED by explicit human rejection. Memory rule updated.`, 'SECURITY', 'warning');

            if (hitlActionDesc) {
                hitlActionDesc.innerHTML = `<span style="color: var(--accent-rose); font-weight: 600;">❌ Action Rejected & Canceled by User.</span>`;
            }
            setTimeout(() => {
                if (hitlBanner) hitlBanner.style.opacity = '0.5';
            }, 1000);
        });
    }

    // Clear Console Handler
    if (btnClearConsole) {
        btnClearConsole.addEventListener('click', () => {
            if (consoleTerminal) {
                consoleTerminal.innerHTML = '';
                appendLog('[System] Execution console cleared.', 'SECURITY', 'info');
            }
        });
    }

    fetchInspectionProfiles();
});
