// ============================================
// TASK UI - Modal Management
// ============================================

let currentTaskId = null;

function openProgressModal(taskId, taskTitle, currentProgress) {
    currentTaskId = taskId;
    
    const modalHtml = `
        <div class="modal-content">
            <h3>Update Progress: ${taskTitle}</h3>
            <p>Current Progress: ${currentProgress}%</p>
            
            <label>New Progress:</label>
            <select id="progressSelect" class="progress-select">
                <option value="0" ${currentProgress === 0 ? 'selected' : ''}>0% - Not Started</option>
                <option value="25" ${currentProgress === 25 ? 'selected' : ''}>25% - Quarter Done</option>
                <option value="50" ${currentProgress === 50 ? 'selected' : ''}>50% - Half Done</option>
                <option value="75" ${currentProgress === 75 ? 'selected' : ''}>75% - Almost Done</option>
                <option value="100" ${currentProgress === 100 ? 'selected' : ''}>100% - Complete</option>
            </select>
            
            <label>Comment:</label>
            <textarea id="progressComment" rows="3" placeholder="What work was done?"></textarea>
            
            <label class="checkbox-label">
                <input type="checkbox" id="waterReleasedCheckbox">
                💧 Water released today
            </label>
            
            <label>📸 Photo:</label>
            <input type="file" id="progressPhoto" accept="image/*" capture="environment">
            
            <label>🎤 Audio:</label>
            <input type="file" id="progressAudio" accept="audio/*" capture="user">
            
            <label>🎥 Video:</label>
            <input type="file" id="progressVideo" accept="video/*" capture="environment">
            
            <div class="modal-actions">
                <button onclick="submitProgress()" class="submit-btn">✓ Submit</button>
                <button onclick="closeProgressModal()" class="cancel-btn">Cancel</button>
            </div>
        </div>
    `;
    
    showModal(modalHtml);
}

async function submitProgress() {
    const newProgress = parseInt(document.getElementById('progressSelect').value);
    const comment = document.getElementById('progressComment').value;
    const waterReleased = document.getElementById('waterReleasedCheckbox')?.checked || false;
    const photoFile = document.getElementById('progressPhoto')?.files[0];
    const audioFile = document.getElementById('progressAudio')?.files[0];
    const videoFile = document.getElementById('progressVideo')?.files[0];
    
    await updateTaskProgress(currentTaskId, newProgress, comment, waterReleased, photoFile, audioFile, videoFile);
}

function closeProgressModal() {
    closeModal();
    currentTaskId = null;
}

// ============ BATCH UPDATE MODAL (Multi-Zone) ============

function openBatchUpdateModal(locationId) {
    fetch(`/tasks/location/${locationId}`)
        .then(res => res.json())
        .then(tasks => {
            const waterTasks = tasks.filter(t => t.task_category === 'water_release');
            
            let html = `
                <div class="modal-content batch-modal">
                    <h3>Batch Update - Water Release Zones</h3>
                    <div class="batch-tasks">
            `;
            
            waterTasks.forEach(task => {
                html += `
                    <div class="batch-task-item">
                        <label>${task.title}</label>
                        <select id="batch_progress_${task.id}">
                            <option value="0">0%</option>
                            <option value="25">25%</option>
                            <option value="50">50%</option>
                            <option value="75">75%</option>
                            <option value="100">100%</option>
                        </select>
                        <input type="checkbox" id="batch_water_${task.id}"> 💧
                    </div>
                `;
            });
            
            html += `
                    </div>
                    <textarea id="batchComment" placeholder="Common comment for all zones..."></textarea>
                    <div class="modal-actions">
                        <button onclick="submitBatchUpdate()">Submit All Updates</button>
                        <button onclick="closeModal()">Cancel</button>
                    </div>
                </div>
            `;
            
            showModal(html);
            window.batchTasks = waterTasks;
        });
}

async function submitBatchUpdate() {
    const updates = [];
    const comment = document.getElementById('batchComment')?.value || '';
    
    for (const task of window.batchTasks) {
        const progressSelect = document.getElementById(`batch_progress_${task.id}`);
        const waterCheckbox = document.getElementById(`batch_water_${task.id}`);
        
        if (progressSelect && progressSelect.value != task.progress_percentage) {
            updates.push({
                task_id: task.id,
                new_progress: parseInt(progressSelect.value),
                comment: comment,
                water_released: waterCheckbox?.checked || false
            });
        }
    }
    
    if (updates.length > 0) {
        await batchUpdateProgress(updates);
    } else {
        showMessage('No changes detected', 'info');
    }
    closeModal();
}

// ============ MODAL HELPERS ============

function showModal(content) {
    let modal = document.getElementById('dynamicModal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'dynamicModal';
        modal.className = 'modal';
        document.body.appendChild(modal);
    }
    modal.innerHTML = content;
    modal.style.display = 'flex';
}

function closeModal() {
    const modal = document.getElementById('dynamicModal');
    if (modal) modal.style.display = 'none';
}

function showMessage(msg, type = 'success') {
    const msgDiv = document.getElementById('message');
    msgDiv.textContent = msg;
    msgDiv.className = `message ${type}`;
    setTimeout(() => {
        msgDiv.className = 'message';
    }, 3000);
}

function viewMedia(url, type) {
    let content = '';
    if (type === 'image') {
        content = `<img src="${url}" style="max-width: 100%; max-height: 80vh;">`;
    } else if (type === 'audio') {
        content = `<audio controls src="${url}" style="width: 100%;"></audio>`;
    } else if (type === 'video') {
        content = `<video controls src="${url}" style="max-width: 100%; max-height: 80vh;"></video>`;
    }
    
    showModal(`
        <div class="modal-content media-viewer">
            ${content}
            <button onclick="closeModal()" style="margin-top: 20px;">Close</button>
        </div>
    `);
}

function closeHistoryModal() {
    closeModal();
}