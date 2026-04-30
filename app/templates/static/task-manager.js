// ============================================
// TASK MANAGER - Core Task Operations
// ============================================


// ============ TASK CRUD OPERATIONS ============

async function createTask() {
    const taskData = {
        title: document.getElementById('taskTitle').value,
        description: document.getElementById('taskDesc').value,
        task_category: document.getElementById('taskCategory').value,
        task_type: document.getElementById('taskType').value,
        time_slot: document.getElementById('taskTimeSlot').value,
        location_id: parseInt(document.getElementById('taskLocationId').value),
        zone_id: document.getElementById('taskZoneId').value ? parseInt(document.getElementById('taskZoneId').value) : null,
        created_by: currentUser.user_id,
        recurring: document.getElementById('taskRecurring').value,
        recurring_interval: document.getElementById('taskIntervalDays').value || null,
        is_zone_based: document.getElementById('taskZoneId').value ? true : false
    };
    
    const response = await fetch('/tasks/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(taskData)
    });
    
    if (response.ok) {
        showMessage('Task created successfully!');
        clearTaskForm();
        loadAllTasks();
        loadManageTasks();
    } else {
        const error = await response.json();
        showMessage(error.detail || 'Failed to create task', 'error');
    }
}

async function loadAllTasks() {
    const locationFilter = document.getElementById('taskLocationFilter')?.value || 'all';
    const typeFilter = document.getElementById('taskTypeFilter')?.value || 'all';
    const datePicker = document.getElementById('adminTaskDatePicker');
    const selectedDate = datePicker?.value || new Date().toISOString().split('T')[0];
    
    try {
        const response = await fetch('/tasks/all');
        let tasks = await response.json();
        
        // Apply filters
        tasks = tasks.filter(task => {
            if (locationFilter !== 'all' && task.location_id != locationFilter) return false;
            if (typeFilter !== 'all' && task.task_category !== typeFilter) return false;
            
            const taskDate = task.due_date ? task.due_date.split('T')[0] : task.created_at.split('T')[0];
            if (taskDate !== selectedDate) return false;
            
            return true;
        });
        
        const container = document.getElementById('allTasksList');
        if (!container) return;
        
        if (tasks.length === 0) {
            container.innerHTML = `<p style="color: #999;">No tasks for ${selectedDate}</p>`;
            return;
        }
        
        // Fetch users for assignment
        const usersRes = await fetch('/users');
        const users = await usersRes.json();
        const workers = users.filter(u => u.role.toLowerCase() === 'worker');
        
        let html = '<div class="task-grid">';
        
        for (const task of tasks) {
            const daysSinceRelease = task.last_water_release_date ? 
                Math.ceil((new Date() - new Date(task.last_water_release_date)) / (1000 * 60 * 60 * 24)) : null;
            
            const statusClass = task.progress_percentage === 100 ? 'completed' : 
                               (task.progress_percentage > 0 ? 'in-progress' : 'pending');
            
            html += `
                <div class="task-card ${statusClass}" data-task-id="${task.id}">
                    <div class="task-header">
                        <h4>${getTaskIcon(task.task_category)} ${task.title}</h4>
                        <span class="task-status">${task.status}</span>
                    </div>
                    
                    <div class="progress-section">
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${task.progress_percentage}%">
                                ${task.progress_percentage}%
                            </div>
                        </div>
                        <div class="progress-stats">
                            <span>Cycle ${task.current_cycle || 1}</span>
                            <span>Day ${getDaysInCycle(task)}</span>
                        </div>
                    </div>
                    
                    ${task.task_category === 'water_release' ? `
                        <div class="water-release-info">
                            <span>💧 Last release: ${daysSinceRelease !== null ? daysSinceRelease + ' days ago' : 'Never'}</span>
                            ${daysSinceRelease > 3 ? '<span class="warning">⚠️ Overdue!</span>' : ''}
                        </div>
                    ` : ''}
                    
                    <div class="task-assignment">
                        <select id="assignSelect_${task.id}" class="assign-select">
                            <option value="">Unassign</option>
                            ${workers.map(w => `<option value="${w.id}" ${task.assigned_to === w.id ? 'selected' : ''}>${w.name}</option>`).join('')}
                        </select>
                        <button onclick="updateTaskAssignment(${task.id})" class="small-btn">Assign</button>
                    </div>
                    
                    <div class="task-actions">
                        <button onclick="openProgressModal(${task.id}, '${task.title.replace(/'/g, "\\'")}', ${task.progress_percentage})" class="update-btn">
                            📊 Update Progress
                        </button>
                        <button onclick="viewTaskHistory(${task.id})" class="history-btn">📜 History</button>
                        ${currentUser?.role === 'admin' ? `<button onclick="deleteTask(${task.id})" class="delete-btn">🗑️</button>` : ''}
                    </div>
                </div>
            `;
        }
        
        html += '</div>';
        container.innerHTML = html;
        
    } catch (error) {
        console.error("Error loading tasks:", error);
        showMessage('Error loading tasks', 'error');
    }
}

// ============ PROGRESS UPDATE ============

async function updateTaskProgress(taskId, newProgress, comment, waterReleased, photoFile, audioFile, videoFile) {
    showMessage("Updating progress...", "success");
    
    let photoUrl = null, audioUrl = null, videoUrl = null;
    
    // Upload media files if provided
    if (photoFile) {
        const formData = new FormData();
        formData.append('file', photoFile);
        const response = await fetch('/upload/photo', { method: 'POST', body: formData });
        if (response.ok) photoUrl = (await response.json()).url;
    }
    
    if (audioFile) {
        const formData = new FormData();
        formData.append('file', audioFile);
        const response = await fetch('/upload/audio', { method: 'POST', body: formData });
        if (response.ok) audioUrl = (await response.json()).url;
    }
    
    if (videoFile) {
        const formData = new FormData();
        formData.append('file', videoFile);
        const response = await fetch('/upload/video', { method: 'POST', body: formData });
        if (response.ok) videoUrl = (await response.json()).url;
    }
    
    const response = await fetch(`/tasks/${taskId}/progress`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            new_progress: newProgress,
            comment: comment,
            water_released: waterReleased,
            photo_url: photoUrl,
            audio_url: audioUrl,
            video_url: videoUrl
        })
    });
    
    if (response.ok) {
        const result = await response.json();
        
        if (result.auto_reset) {
            showMessage(result.auto_reset.message, 'success');
        } else {
            showMessage(`Progress updated to ${newProgress}%!`, 'success');
        }
        
        closeProgressModal();
        loadAllTasks();
        loadWorkerTasks();
        
    } else {
        const error = await response.json();
        showMessage(error.detail || 'Failed to update progress', 'error');
    }
}

// ============ BATCH UPDATE (Multi-Zone Same Day) ============

async function batchUpdateProgress(updates) {
    const response = await fetch('/tasks/batch-progress', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ updates: updates })
    });
    
    if (response.ok) {
        const result = await response.json();
        showMessage(`Updated ${result.updates.filter(u => u.success).length} tasks!`, 'success');
        loadAllTasks();
        loadWorkerTasks();
    } else {
        showMessage('Batch update failed', 'error');
    }
}

// ============ TASK HISTORY ============

async function viewTaskHistory(taskId) {
    const historyRes = await fetch(`/tasks/${taskId}/progress-history`);
    const cyclesRes = await fetch(`/tasks/${taskId}/cycles-history`);
    
    const history = await historyRes.json();
    const cycles = await cyclesRes.json();
    
    let html = `
        <div class="history-modal">
            <h3>Task History</h3>
            <h4>Completed Cycles</h4>
            <table class="history-table">
                <tr><th>Cycle</th><th>Days Taken</th><th>Completed</th></tr>
                ${cycles.map(c => `
                    <tr><td>${c.cycle}</td><td>${c.days_taken} days</td><td>${new Date(c.end_date).toLocaleDateString()}</td></tr>
                `).join('')}
            </table>
            
            <h4>Progress Updates</h4>
            <table class="history-table">
                <tr><th>Date</th><th>Progress</th><th>Water Released</th><th>Comment</th></tr>
                ${history.map(h => `
                    <tr>
                        <td>${new Date(h.created_at).toLocaleDateString()}</td>
                        <td>${h.old_progress}% → ${h.new_progress}%</td>
                        <td>${h.water_released ? '✅ Yes' : '❌ No'}</td>
                        <td>${h.comment || '-'}</td>
                    </tr>
                `).join('')}
            </table>
            <button onclick="closeHistoryModal()">Close</button>
        </div>
    `;
    
    showModal(html);
}

// ============ WORKER TASKS ============

async function loadWorkerTasks() {
    if (!currentUser) return;
    
    const typeFilter = document.getElementById('workerTaskTypeFilter')?.value || 'all';
    const today = new Date().toISOString().split('T')[0];
    
    try {
        const response = await fetch(`/tasks/user/${currentUser.user_id}`);
        let tasks = await response.json();
        
        tasks = tasks.filter(task => {
            const taskDate = task.due_date ? task.due_date.split('T')[0] : task.created_at.split('T')[0];
            if (taskDate !== today) return false;
            if (typeFilter !== 'all' && task.task_category !== typeFilter) return false;
            return true;
        });
        
        const container = document.getElementById('workerTasksList');
        if (!container) return;
        
        if (tasks.length === 0) {
            container.innerHTML = '<p>No tasks for today</p>';
            return;
        }
        
        let html = '<div class="task-grid">';
        
        for (const task of tasks) {
            html += `
                <div class="task-card">
                    <h4>${getTaskIcon(task.task_category)} ${task.title}</h4>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${task.progress_percentage || 0}%">
                            ${task.progress_percentage || 0}%
                        </div>
                    </div>
                    <button onclick="openProgressModal(${task.id}, '${task.title.replace(/'/g, "\\'")}', ${task.progress_percentage || 0})" class="update-btn">
                        Update Progress
                    </button>
                </div>
            `;
        }
        
        html += '</div>';
        container.innerHTML = html;
        
    } catch (error) {
        console.error("Error loading worker tasks:", error);
    }
}

// ============ HELPER FUNCTIONS ============

function getTaskIcon(category) {
    const icons = {
        'water_release': '💧',
        'fertilizer': '🌱',
        'grass_cutting': '✂️',
        'general': '📋'
    };
    return icons[category] || '📋';
}

function getDaysInCycle(task) {
    if (!task.cycle_start_date) return 0;
    const start = new Date(task.cycle_start_date);
    const now = new Date();
    return Math.ceil((now - start) / (1000 * 60 * 60 * 24));
}

async function updateTaskAssignment(taskId) {
    const select = document.getElementById(`assignSelect_${taskId}`);
    const assignedTo = select.value;
    
    const response = await fetch(`/tasks/assign/${taskId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ assigned_to: assignedTo ? parseInt(assignedTo) : null })
    });
    
    if (response.ok) {
        showMessage('Task assigned successfully!');
        loadAllTasks();
    } else {
        showMessage('Failed to assign task', 'error');
    }
}

async function deleteTask(taskId) {
    if (confirm('Delete this task?')) {
        const response = await fetch(`/tasks/delete/${taskId}`, { method: 'DELETE' });
        if (response.ok) {
            showMessage('Task deleted');
            loadAllTasks();
            loadManageTasks();
        } else {
            showMessage('Delete failed', 'error');
        }
    }
}

function clearTaskForm() {
    document.getElementById('taskTitle').value = '';
    document.getElementById('taskDesc').value = '';
    document.getElementById('taskIntervalDays').value = '';
    document.getElementById('intervalDaysDiv').style.display = 'none';
}

function toggleRecurringOptions() {
    const recurring = document.getElementById('taskRecurring').value;
    document.getElementById('intervalDaysDiv').style.display = recurring === 'interval' ? 'block' : 'none';
}