// ============================================
// TASK REPORTS - Water Release Analytics
// ============================================

async function generateWaterReport() {
    const locationId = document.getElementById('reportLocationId').value;
    const startDate = document.getElementById('reportStartDate').value;
    const endDate = document.getElementById('reportEndDate').value;
    
    if (!locationId) {
        showMessage('Please select a location', 'error');
        return;
    }
    
    let url = `/tasks/water-release-report/${locationId}`;
    if (startDate) url += `?start_date=${startDate}`;
    if (endDate) url += `${startDate ? '&' : '?'}end_date=${endDate}`;
    
    const response = await fetch(url);
    const report = await response.json();
    
    const container = document.getElementById('reportResults');
    
    let html = `
        <div class="report-container">
            <h3>Water Release Report</h3>
            <p>Generated: ${new Date(report.report_date).toLocaleString()}</p>
            
            <div class="report-summary">
                <div class="summary-card">
                    <h4>Total Zones</h4>
                    <p>${report.tasks.length}</p>
                </div>
                <div class="summary-card">
                    <h4>Active Zones</h4>
                    <p>${report.tasks.filter(t => t.current_progress > 0 && t.current_progress < 100).length}</p>
                </div>
                <div class="summary-card">
                    <h4>Completed Cycles</h4>
                    <p>${report.tasks.reduce((sum, t) => sum + (t.total_cycles_completed || 0), 0)}</p>
                </div>
            </div>
    `;
    
    for (const task of report.tasks) {
        const overdueClass = task.days_since_last_water_release > 3 ? 'overdue' : '';
        
        html += `
            <div class="zone-report-card ${overdueClass}">
                <h4>${task.title}</h4>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${task.current_progress}%">
                        ${task.current_progress}%
                    </div>
                </div>
                <div class="report-details">
                    <div>📅 Current Cycle: Day ${task.days_in_current_cycle}</div>
                    <div>💧 Last Release: ${task.days_since_last_water_release !== null ? task.days_since_last_water_release + ' days ago' : 'Never'}</div>
                    <div>🔄 Total Cycles: ${task.total_cycles_completed}</div>
                </div>
                
                ${task.cycle_history.length > 0 ? `
                    <details>
                        <summary>Previous Cycles</summary>
                        <table class="history-table">
                            <tr><th>Cycle</th><th>Days Taken</th><th>Completed Date</th></tr>
                            ${task.cycle_history.map(c => `
                                <tr>
                                    <td>Cycle ${c.cycle}</td>
                                    <td>${c.days_taken} days</td>
                                    <td>${new Date(c.completed_at).toLocaleDateString()}</td>
                                </tr>
                            `).join('')}
                        </table>
                    </details>
                ` : ''}
            </div>
        `;
    }
    
    html += '</div>';
    container.innerHTML = html;
    
    // Store report data for CSV export
    window.currentReport = report;
}

function exportReportToCSV() {
    if (!window.currentReport) {
        showMessage('Generate a report first', 'error');
        return;
    }
    
    let csv = 'Zone,Current Progress,Cycle Day,Last Release (days),Total Cycles\n';
    
    for (const task of window.currentReport.tasks) {
        csv += `"${task.title}",${task.current_progress}%,${task.days_in_current_cycle},${task.days_since_last_water_release || 'N/A'},${task.total_cycles_completed}\n`;
    }
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `water_report_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
    
    showMessage('Report exported!', 'success');
}

// ============ TASK HISTORY VIEW ============

async function showTaskHistory(taskId) {
    const historyRes = await fetch(`/tasks/${taskId}/progress-history`);
    const cyclesRes = await fetch(`/tasks/${taskId}/cycles-history`);
    
    const history = await historyRes.json();
    const cycles = await cyclesRes.json();
    
    let html = `
        <div class="modal-content history-modal-large">
            <h3>📊 Task Performance History</h3>
            
            <div class="stats-grid">
                <div class="stat">Total Cycles: ${cycles.length}</div>
                <div class="stat">Avg Days/Cycle: ${calculateAvgDays(cycles)}</div>
                <div class="stat">Best Cycle: ${getBestCycle(cycles)} days</div>
            </div>
            
            <h4>Cycle Timeline</h4>
            <div class="timeline">
                ${cycles.map(c => `
                    <div class="timeline-item">
                        <div class="timeline-badge">Cycle ${c.cycle}</div>
                        <div class="timeline-content">
                            Started: ${new Date(c.start_date).toLocaleDateString()}<br>
                            Completed: ${new Date(c.end_date).toLocaleDateString()}<br>
                            Took: ${c.days_taken} days
                        </div>
                    </div>
                `).join('')}
            </div>
            
            <h4>Daily Progress Log</h4>
            <div class="progress-log">
                ${history.map(h => `
                    <div class="log-entry">
                        <span class="log-date">${new Date(h.created_at).toLocaleDateString()}</span>
                        <span class="log-progress">${h.old_progress}% → ${h.new_progress}%</span>
                        <span class="log-water">${h.water_released ? '💧' : '⭕'}</span>
                        <span class="log-comment">${h.comment || '-'}</span>
                    </div>
                `).join('')}
            </div>
            
            <button onclick="closeModal()">Close</button>
        </div>
    `;
    
    showModal(html);
}

function calculateAvgDays(cycles) {
    if (cycles.length === 0) return 0;
    const sum = cycles.reduce((acc, c) => acc + c.days_taken, 0);
    return Math.round(sum / cycles.length);
}

function getBestCycle(cycles) {
    if (cycles.length === 0) return 0;
    return Math.min(...cycles.map(c => c.days_taken));
}