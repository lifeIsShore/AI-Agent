document.addEventListener('DOMContentLoaded', () => {
    initPowerSwitch();
    initDocumentHub();
    initMissionConsole();
    initHITLApprovalCenter();
    initClearConsole();
});

let systemDocuments = {};

function initPowerSwitch() {
    const btn = document.getElementById('btn-toggle-system');
    if (!btn) return;

    btn.addEventListener('click', async () => {
        try {
            const resp = await fetch('/api/system/toggle', { method: 'POST' });
            const data = await resp.json();
            updatePowerSwitchUI(data.system_running, data.display_text);
            logConsoleEvent(`[PowerSwitch] System state toggled to: ${data.display_text}`, data.system_running ? 'success' : 'warning');
        } catch (err) {
            console.error('Failed to toggle power switch:', err);
        }
    });

    fetchSystemStatus();
}

async function fetchSystemStatus() {
    try {
        const resp = await fetch('/api/status');
        const data = await resp.json();
        updatePowerSwitchUI(data.system_running, data.display_text);
    } catch (err) {
        console.error('Failed to fetch status:', err);
    }
}

function updatePowerSwitchUI(isRunning, displayText) {
    const btn = document.getElementById('btn-toggle-system');
    const textSpan = document.getElementById('power-switch-text');
    const statusText = document.getElementById('os-status-text');
    const statusPill = document.getElementById('status-pill-container');
    const statusDot = document.getElementById('status-dot-indicator');

    if (isRunning) {
        btn.className = 'power-switch-btn running';
        textSpan.textContent = 'STOP SYSTEM';
        statusText.textContent = displayText || 'SYSTEM RUNNING (BOUNDED_AUTO)';
        statusPill.className = 'status-pill online';
        statusDot.className = 'status-dot pulse green';
    } else {
        btn.className = 'power-switch-btn stopped';
        textSpan.textContent = 'START SYSTEM';
        statusText.textContent = displayText || 'SYSTEM STOPPED (HALTED)';
        statusPill.className = 'status-pill stopped';
        statusDot.className = 'status-dot red';
    }
}

function initMissionConsole() {
    const planBtn = document.getElementById('btn-plan-mission');
    const execBtn = document.getElementById('btn-execute-mission');
    const inputField = document.getElementById('mission-prompt-input');

    if (planBtn) {
        planBtn.addEventListener('click', () => submitMission('PLAN'));
    }
    if (execBtn) {
        execBtn.addEventListener('click', () => submitMission('EXECUTE'));
    }
}

async function submitMission(mode) {
    const inputField = document.getElementById('mission-prompt-input');
    const prompt = inputField ? inputField.value.trim() : '';
    if (!prompt) return;

    try {
        const resp = await fetch('/api/missions/submit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt, mode })
        });
        const data = await resp.json();
        logConsoleEvent(`[MissionConsole] Mission Submitted (${mode}): '${prompt}'`, 'highlight');
        renderMissionTimeline(data.mission);
    } catch (err) {
        console.error('Failed to submit mission:', err);
    }
}

function renderMissionTimeline(mission) {
    const container = document.getElementById('mission-timeline-container');
    if (!container || !mission || !mission.pipeline_steps) return;

    container.innerHTML = mission.pipeline_steps.map(step => `
        <div class="m-step-item ${step.status.toLowerCase()}">
            <span class="m-step-icon">${step.status === 'COMPLETED' ? '✓' : step.status === 'APPROVED' ? '🛡️' : '⚙️'}</span>
            <span class="m-step-title font-cyan">[${step.agent}] ${step.task}</span>
        </div>
    `).join('');
}

function initHITLApprovalCenter() {
    const approveBtn = document.getElementById('btn-approve-action');
    const rejectBtn = document.getElementById('btn-reject-action');

    if (approveBtn) {
        approveBtn.addEventListener('click', () => respondHITL('APPROVE'));
    }
    if (rejectBtn) {
        rejectBtn.addEventListener('click', () => respondHITL('REJECT'));
    }
}

async function respondHITL(decision) {
    try {
        const resp = await fetch('/api/hitl/respond', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ decision, proposal_id: 'prop_99182a' })
        });
        const data = await resp.json();
        logConsoleEvent(`[HITLApproval] Action ${decision} recorded for proposal ${data.proposal_id}`, decision === 'APPROVE' ? 'success' : 'warning');
        alert(`HITL Decision '${decision}' recorded successfully.`);
    } catch (err) {
        console.error('Failed to respond to HITL:', err);
    }
}

function initDocumentHub() {
    const tabs = document.querySelectorAll('.doc-tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            const category = tab.getAttribute('data-cat');
            renderCategoryDocument(category);
        });
    });

    fetchDocuments();
}

async function fetchDocuments() {
    try {
        const resp = await fetch('/api/documents/categories');
        const data = await resp.json();
        systemDocuments = data.categories || {};
        renderCategoryDocument('coding');
    } catch (err) {
        console.error('Failed to fetch documents:', err);
    }
}

function renderCategoryDocument(category) {
    const titleEl = document.getElementById('doc-file-title');
    const bodyEl = document.getElementById('doc-file-body');
    if (!titleEl || !bodyEl) return;

    const list = systemDocuments[category] || [];
    if (list.length > 0) {
        const doc = list[0];
        titleEl.textContent = `📁 ${doc.path.replace(/\\/g, '/')}`;
        bodyEl.textContent = doc.content;
    } else {
        titleEl.textContent = `📁 docs/${category}/`;
        bodyEl.textContent = `No markdown documents found in docs/${category}/ directory.`;
    }
}

function initClearConsole() {
    const btn = document.getElementById('btn-clear-console');
    const terminal = document.getElementById('console-terminal');
    if (btn && terminal) {
        btn.addEventListener('click', () => {
            terminal.innerHTML = '';
        });
    }
}

function logConsoleEvent(msg, type = 'info') {
    const terminal = document.getElementById('console-terminal');
    if (!terminal) return;
    const timeStr = new Date().toLocaleTimeString();
    const div = document.createElement('div');
    div.className = `log-line ${type}`;
    div.textContent = `[${timeStr}] ${msg}`;
    terminal.appendChild(div);
    terminal.scrollTop = terminal.scrollHeight;
}
