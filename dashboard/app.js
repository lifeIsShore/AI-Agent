document.addEventListener('DOMContentLoaded', () => {
    initPowerSwitch();
    initDocumentHub();
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
