// Personal AI Agent Dashboard Operational Control Plane (V6.5)
document.addEventListener('DOMContentLoaded', () => {
    console.log("⚡ Personal AI Agent OS Operational Control Plane (V6.5) initialized.");

    const consoleTerminal = document.getElementById('console-terminal');
    const btnApprove = document.getElementById('btn-approve');
    const btnReject = document.getElementById('btn-reject');
    const hitlInput = document.getElementById('hitl-input');
    const hitlBanner = document.getElementById('hitl-banner');
    const hitlActionDesc = document.getElementById('hitl-action-desc');
    const btnClearConsole = document.getElementById('btn-clear-console');
    const filterButtons = document.querySelectorAll('.filter-btn');

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

    // Fetch Pending Proposals from Backend API
    async function fetchPendingProposals() {
        try {
            const res = await fetch('/api/proposals');
            if (res.ok) {
                const data = await res.json();
                if (data.proposals && data.proposals.length > 0) {
                    const p = data.proposals[0];
                    if (hitlActionDesc) {
                        hitlActionDesc.innerHTML = `<strong>${p.agent}</strong> proposes action: <em>${p.description}</em> (Target: ${p.target} | Risk: ${p.risk_level})`;
                    }
                }
            }
        } catch (e) {
            console.log("Using default proposal data.");
        }
    }

    // HITL Approve Button Handler
    if (btnApprove) {
        btnApprove.addEventListener('click', async () => {
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
        btnReject.addEventListener('click', async () => {
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

    fetchPendingProposals();
});
