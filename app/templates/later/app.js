let currentUser = null;
let editingUserId = null;
let currentTaskId = null;
const API_URL = "";

function showMessage(msg, type = "success") {
    const msgDiv = document.getElementById("message");
    msgDiv.textContent = msg;
    msgDiv.className = `message ${type}`;
    setTimeout(() => {
        msgDiv.className = "message";
    }, 3000);
}

function getCurrentTimeSlot() {
    const hour = new Date().getHours();
    if (hour >= 6 && hour < 12) return "morning";
    else if (hour >= 18 && hour < 22) return "night";
    else return "anytime";
}

function showSection(sectionName) {
    if (sectionName === 'admin' && currentUser.role === 'worker') {
        showMessage("Access denied", "error");
        return;
    }
    document.getElementById("tasksSection").classList.remove("active");
    document.getElementById("locationsSection").classList.remove("active");
    document.getElementById("reportIssueSection").classList.remove("active");
    document.getElementById("adminSection").classList.remove("active");

    document.getElementById(`${sectionName}Section`).classList.add("active");
    
    if (sectionName === "locations") loadLocations();
    if (sectionName === "reportIssue") loadLocations();
    if (sectionName === "tasks") loadTasks();
    if (sectionName === "admin") {
        if (currentUser.role !== "admin" && currentUser.role !== "supervisor" && currentUser.role !== "Admin") {
            showMessage("Access denied. Admin or Supervisor only.", "error");
            return;
        }
        loadAllUsers();
        loadLocationsForDropdowns();
    }
}

async function login() {
    const username = document.getElementById("loginUsername").value;
    const password = document.getElementById("loginPassword").value;

    try {
        const response = await fetch(`${API_URL}/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password })
        });

        if (response.ok) {
            currentUser = await response.json();
            document.getElementById("userName").textContent = currentUser.name;
            document.getElementById("userRole").textContent = currentUser.role;
            
            document.getElementById("loginSection").classList.remove("active");
            document.getElementById("appSection").classList.add("active");
            document.getElementById("bottomNav").style.display = "flex";
            
            if (currentUser.role.toLowerCase() === "admin" || currentUser.role.toLowerCase() === "supervisor") {
                const adminBtn = document.getElementById("adminBtn");
                if (adminBtn) adminBtn.style.display = "block";
            } else {
                const adminBtn = document.getElementById("adminBtn");
                if (adminBtn) adminBtn.style.display = "none";
            }
            
            showMessage(`Welcome ${currentUser.name}!`);
            
            const quickActionsCard = document.getElementById("quickActionsCard");
            if (quickActionsCard) {
                if (currentUser.role.toLowerCase() === "admin" || currentUser.role.toLowerCase() === "supervisor") {
                    quickActionsCard.style.display = "none";
                    showSection('admin');
                    loadAllTasks();
                } else {
                    quickActionsCard.style.display = "block";
                    showSection('tasks');
                }
            }

            loadLocations();
            loadTasks();
            loadLocationsForDropdowns();
        } else {
            const error = await response.json();
            showMessage(error.detail || "Login failed", "error");
        }
    } catch (err) {
        showMessage("Network error. Is the server running?", "error");
    }
}

async function loadLocations() {
    try {
        const response = await fetch(`${API_URL}/locations/all`);
        if (response.ok) {
            const locations = await response.json();
            const locationsDiv = document.getElementById("locationsList");
            const issueLocationSelect = document.getElementById("issueLocation");
            
            locationsDiv.innerHTML = "";
            issueLocationSelect.innerHTML = '<option value="">Select Location</option>';
            
            locations.forEach(loc => {
                locationsDiv.innerHTML += `
                    <div class="location-item">
                        <strong>${loc.name}</strong>
                        ${loc.area_acres > 0 ? `${loc.area_acres} Acres` : ''}
                        <small>${loc.region}</small>
                    </div>
                `;
                issueLocationSelect.innerHTML += `<option value="${loc.id}">${loc.name} (${loc.region})</option>`;
            });
        }
    } catch (err) {
        console.error("Error loading locations:", err);
    }
}

async function loadTasks() {
    if (!currentUser) return;
    
    const showAll = document.getElementById("showAllTasks")?.checked || false;
    const currentSlot = getCurrentTimeSlot();
    
    try {
        const response = await fetch(`${API_URL}/tasks/user/${currentUser.user_id}`);
        if (response.ok) {
            let tasks = await response.json();
            
            if (!showAll && currentSlot !== "anytime") {
                tasks = tasks.filter(task => 
                    task.time_slot === currentSlot || task.time_slot === "anytime"
                );
            }
            
            const tasksDiv = document.getElementById("tasksList");
            
            if (tasks.length === 0) {
                tasksDiv.innerHTML = '<p style="color: #999;">No tasks assigned for this time slot</p>';
                return;
            }
            
            tasksDiv.innerHTML = "";
            tasks.forEach(task => {
                const statusColor = task.status === "completed" ? "#4CAF50" : "#ff9800";
                const timeBadge = task.time_slot === "morning" ? "🌅 Morning" : 
                                (task.time_slot === "night" ? "🌙 Night" : "🕐 Anytime");
                
                tasksDiv.innerHTML += `
                    <div class="task-item" style="border-left-color: ${statusColor};">
                        <strong>${task.title}</strong>
                        <p style="font-size: 12px; color: #666;">${task.description || "No description"}</p>
                        <p style="font-size: 11px; margin-top: 8px;">
                            <span style="background: #f0f0f0; padding: 2px 8px; border-radius: 10px;">${timeBadge}</span>
                            Status: <span style="color: ${statusColor}; font-weight: bold;">${task.status}</span>
                            ${task.due_date ? ` | Due: ${new Date(task.due_date).toLocaleDateString()}` : ''}
                        </p>
                        ${task.status !== "completed" ? `
                            <button onclick="openCompletionModal(${task.id}, '${task.title.replace(/'/g, "\\'")}')" style="margin-top: 8px; padding: 8px; font-size: 12px; background: #4CAF50;">
                                📸 Complete with Media
                            </button>
                        ` : `
                            <p style="margin-top: 8px; font-size: 11px; color: green;">✓ Completed</p>
                        `}
                    </div>
                `;
            });
        }
    } catch (err) {
        console.error("Error loading tasks:", err);
    }
}

async function loadAllTasks() {
    console.log("Loading tasks...");
    try {
        const response = await fetch('/tasks/all');
        const tasks = await response.json();
        console.log("Tasks found:", tasks);
        
        const container = document.getElementById('allTasksList');
        
        if (!container) {
            console.error("allTasksList not found");
            return;
        }
        
        if (tasks.length === 0) {
            container.innerHTML = '<p style="color: #999;">No tasks added yet</p>';
            return;
        }
        
        let html = '<table><tr style="background: #f0f0f0;"><th>ID</th><th>Title</th><th>Description</th><th>Assigned To</th><th>Time Slot</th><th>Status</th><th>Actions</th></tr>';
        
        for (const task of tasks) {
            let assignedToName = 'Unassigned';
            if (task.assigned_to) {
                const usersRes = await fetch('/users');
                const users = await usersRes.json();
                const assignedUser = users.find(u => u.id === task.assigned_to);
                assignedToName = assignedUser ? assignedUser.name : 'Unknown';
            }
            
            html += `
                <tr>
                    <td>${task.id}</td>
                    <td><strong>${task.title}</strong></td>
                    <td>${task.description || '-'}</td>
                    <td>${assignedToName}</td>
                    <td>${task.time_slot}</td>
                    <td><span style="background: ${task.status === 'completed' ? '#4CAF50' : '#ff9800'}; color: white; padding: 2px 8px; border-radius: 10px;">${task.status}</span></td>
                    <td>
                        <button onclick="openCompletionModal(${task.id}, '${task.title.replace(/'/g, "\\'")}')" style="background: #4CAF50; padding: 5px 10px; width: auto; margin-right: 5px;">📸 Complete</button>
                        <button onclick="deleteTask(${task.id})" style="background: #f44336; padding: 5px 10px; width: auto;">🗑️ Delete</button>
                    </td>
                </tr>
            `;
        }
        html += '</table>';
        container.innerHTML = html;
        console.log("✅ Tasks displayed:", tasks.length);
    } catch (error) {
        console.error("Error loading tasks:", error);
        container.innerHTML = '<p style="color: red;">Error loading tasks</p>';
    }
}

async function deleteTask(taskId) {
    if (confirm('Are you sure you want to delete this task?')) {
        const response = await fetch(`/tasks/delete/${taskId}`, { method: 'DELETE' });
        if (response.ok) {
            showMessage('Task deleted successfully!');
            loadAllTasks();
            loadTasks();
        } else {
            showMessage('Failed to delete task', 'error');
        }
    }
}

async function loadAllUsers() {
    try {
        const response = await fetch('/users');
        if (!response.ok) return;
        
        const users = await response.json();
        const usersDiv = document.getElementById('allUsersList');
        
        if (!usersDiv) return;
        
        if (users.length === 0) {
            usersDiv.innerHTML = '<p style="color: #999;">No users found</p>';
            return;
        }
        
        let html = '<table><tr style="background: #f0f0f0;"><th>Name</th><th>Role</th><th>Username</th><th>Region</th><th>Actions</th></tr>';
        
        users.forEach(user => {
            html += `
                <tr>
                    <td>${user.name}</td>
                    <td>${user.role}</td>
                    <td>${user.username}</td>
                    <td>${user.region || '-'}</td>
                    <td>
                        <button onclick="editUser(${user.id})" style="background: #2196F3; padding: 5px 10px; width: auto; margin-right: 5px;">✏️ Edit</button>
                        <button onclick="deleteUser(${user.id})" style="background: #f44336; padding: 5px 10px; width: auto;">🗑️ Delete</button>
                    </td>
                </tr>
            `;
        });
        html += '</table>';
        usersDiv.innerHTML = html;
        console.log("✅ Users displayed:", users.length);
    } catch (error) {
        console.error("Error loading users:", error);
    }
}

async function deleteUser(userId) {
    if (confirm('Are you sure you want to delete this user?')) {
        const response = await fetch(`/user/delete/${userId}`, { method: 'DELETE' });
        if (response.ok) {
            showMessage('User deleted successfully!');
            loadAllUsers();
        } else {
            showMessage('Failed to delete user', 'error');
        }
    }
}

async function editUser(userId) {
    editingUserId = userId;
    const response = await fetch(`/user/${userId}`);
    if (response.ok) {
        const user = await response.json();
        document.getElementById('editUserName').value = user.name;
        document.getElementById('editUserRole').value = user.role;
        document.getElementById('editUserRegion').value = user.region || '';
        document.getElementById('editUserPhone').value = user.phone || '';
        document.getElementById('editUserPassword').value = '';
        document.getElementById('editUserModal').style.display = 'block';
    }
}

async function updateUser() {
    const userData = {
        name: document.getElementById('editUserName').value,
        role: document.getElementById('editUserRole').value,
        region: document.getElementById('editUserRegion').value,
        phone: document.getElementById('editUserPhone').value,
        password: document.getElementById('editUserPassword').value || null
    };
    
    const response = await fetch(`/user/update/${editingUserId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userData)
    });
    
    if (response.ok) {
        showMessage('User updated successfully!');
        document.getElementById('editUserModal').style.display = 'none';
        loadAllUsers();
    } else {
        showMessage('Failed to update user', 'error');
    }
}

function closeEditModal() {
    document.getElementById('editUserModal').style.display = 'none';
}

async function loadAllZones() {
    const response = await fetch('/zones/all');
    if (response.ok) {
        const zones = await response.json();
        const container = document.getElementById('allZonesList');
        
        if (zones.length === 0) {
            container.innerHTML = '<p style="color: #999;">No zones added yet</p>';
            return;
        }
        
        let html = '<table>';
        zones.forEach(zone => {
            html += `
                <tr>
                    <td><strong>${zone.name}</strong></td>
                    <td>${zone.area_acres || 0} acres</td>
                    <td>Location ID: ${zone.location_id}</td>
                </tr>
            `;
        });
        html += '</table>';
        container.innerHTML = html;
    }
}

async function loadZonesForManage() {
    const locationId = document.getElementById('manageZoneLocationId').value;
    if (!locationId) return;
    
    const response = await fetch(`/zones/location/${locationId}`);
    if (response.ok) {
        const zones = await response.json();
        const zoneSelect = document.getElementById('manageZoneSelect');
        zoneSelect.innerHTML = '<option value="">Select Zone</option>';
        zones.forEach(zone => {
            zoneSelect.innerHTML += `<option value="${zone.id}" data-name="${zone.name}" data-area="${zone.area_acres || 0}">${zone.name} (${zone.area_acres || 0} acres)</option>`;
        });
        document.getElementById('zoneDetails').style.display = 'none';
    }
}

function showZoneDetails() {
    const select = document.getElementById('manageZoneSelect');
    const selectedOption = select.options[select.selectedIndex];
    const zoneId = select.value;
    
    if (zoneId) {
        document.getElementById('editZoneName').value = selectedOption.getAttribute('data-name');
        document.getElementById('editZoneArea').value = selectedOption.getAttribute('data-area');
        document.getElementById('zoneDetails').style.display = 'block';
        document.getElementById('zoneDetails').setAttribute('data-zone-id', zoneId);
    } else {
        document.getElementById('zoneDetails').style.display = 'none';
    }
}

async function updateZone() {
    const zoneId = document.getElementById('zoneDetails').getAttribute('data-zone-id');
    const newName = document.getElementById('editZoneName').value;
    const newArea = document.getElementById('editZoneArea').value;
    const locationId = document.getElementById('manageZoneLocationId').value;
    
    if (!newName) {
        showMessage('Please enter zone name', 'error');
        return;
    }
    
    const response = await fetch(`/zones/update/${zoneId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            name: newName,
            area_acres: parseFloat(newArea) || 0,
            location_id: parseInt(locationId)
        })
    });
    
    if (response.ok) {
        showMessage('Zone updated successfully!');
        loadZonesForManage();
        document.getElementById('zoneDetails').style.display = 'none';
    } else {
        showMessage('Failed to update zone', 'error');
    }
}

async function deleteZone() {
    const zoneId = document.getElementById('zoneDetails').getAttribute('data-zone-id');
    const zoneName = document.getElementById('editZoneName').value;
    
    if (confirm(`Are you sure you want to delete zone "${zoneName}"?`)) {
        const response = await fetch(`/zones/delete/${zoneId}`, { method: 'DELETE' });
        if (response.ok) {
            showMessage('Zone deleted successfully!');
            loadZonesForManage();
            document.getElementById('zoneDetails').style.display = 'none';
            document.getElementById('manageZoneSelect').innerHTML = '<option value="">Select Zone</option>';
        } else {
            showMessage('Failed to delete zone', 'error');
        }
    }
}

async function loadLocationsForDropdowns() {
    const response = await fetch('/locations/all');
    if (response.ok) {
        const locations = await response.json();
        
        const zoneLocationSelect = document.getElementById('zoneLocationId');
        if (zoneLocationSelect) {
            zoneLocationSelect.innerHTML = '<option value="">Select Location</option>';
            locations.forEach(loc => {
                zoneLocationSelect.innerHTML += `<option value="${loc.id}">${loc.name} (${loc.region})</option>`;
            });
        }
        
        const manageZoneLocationSelect = document.getElementById('manageZoneLocationId');
        if (manageZoneLocationSelect) {
            manageZoneLocationSelect.innerHTML = '<option value="">Select Location</option>';
            locations.forEach(loc => {
                manageZoneLocationSelect.innerHTML += `<option value="${loc.id}">${loc.name} (${loc.region})</option>`;
            });
        }
        
        const taskLocationSelect = document.getElementById('taskLocationId');
        if (taskLocationSelect) {
            taskLocationSelect.innerHTML = '<option value="">Select Location</option>';
            locations.forEach(loc => {
                taskLocationSelect.innerHTML += `<option value="${loc.id}">${loc.name} (${loc.region})</option>`;
            });
        }
        
        const contactLocationSelect = document.getElementById('contactLocationId');
        if (contactLocationSelect) {
            contactLocationSelect.innerHTML = '<option value="">Select Location</option>';
            locations.forEach(loc => {
                contactLocationSelect.innerHTML += `<option value="${loc.id}">${loc.name} (${loc.region})</option>`;
            });
        }
        
        const taskAssignedTo = document.getElementById('taskAssignedTo');
        if (taskAssignedTo) {
            const usersResponse = await fetch('/users');
            if (usersResponse.ok) {
                const users = await usersResponse.json();
                taskAssignedTo.innerHTML = '<option value="">Select User</option>';
                users.forEach(user => {
                    taskAssignedTo.innerHTML += `<option value="${user.id}">${user.name} (${user.role})</option>`;
                });
            }
        }
    }
}

function showAdminTab(tabName) {
    const tabs = ['addTask', 'addLocation', 'addZone', 'manageZones', 'viewZones', 'addContact', 'viewUsers', 'viewTasks', 'addUser'];
    
    tabs.forEach(tab => {
        const element = document.getElementById(`${tab}Form`);
        if (element) element.style.display = 'none';
    });
    
    const selectedTab = document.getElementById(`${tabName}Form`);
    if (selectedTab) selectedTab.style.display = 'block';
    
    if (tabName === 'viewZones') loadAllZones();
    if (tabName === 'viewUsers') loadAllUsers();
    if (tabName === 'viewTasks') loadAllTasks();
    if (tabName === 'manageZones') loadLocationsForDropdowns();
}

function openCompletionModal(taskId, taskTitle) {
    currentTaskId = taskId;
    document.getElementById('completionTaskTitle').textContent = taskTitle;
    document.getElementById('completionTaskId').value = taskId;
    document.getElementById('completionNotes').value = '';
    document.getElementById('completionPhoto').value = '';
    document.getElementById('completionAudio').value = '';
    document.getElementById('completionVideo').value = '';
    document.getElementById('completionModal').style.display = 'block';
}

function closeCompletionModal() {
    document.getElementById('completionModal').style.display = 'none';
    currentTaskId = null;
}

async function submitTaskCompletion() {
    const taskId = document.getElementById('completionTaskId').value;
    const notes = document.getElementById('completionNotes').value;
    const photoFile = document.getElementById('completionPhoto').files[0];
    const audioFile = document.getElementById('completionAudio').files[0];
    const videoFile = document.getElementById('completionVideo').files[0];
    
    if (!taskId) {
        showMessage("No task selected", "error");
        return;
    }
    
    let photoUrl = null, audioUrl = null, videoUrl = null;
    
    if (photoFile || audioFile || videoFile) {
        showMessage("Uploading media...", "success");
    }
    
    if (photoFile) {
        const formData = new FormData();
        formData.append('file', photoFile);
        const response = await fetch('/upload/photo', { method: 'POST', body: formData });
        if (response.ok) {
            const result = await response.json();
            photoUrl = result.url;
        }
    }
    
    if (audioFile) {
        const formData = new FormData();
        formData.append('file', audioFile);
        const response = await fetch('/upload/audio', { method: 'POST', body: formData });
        if (response.ok) {
            const result = await response.json();
            audioUrl = result.url;
        }
    }
    
    if (videoFile) {
        const formData = new FormData();
        formData.append('file', videoFile);
        const response = await fetch('/upload/video', { method: 'POST', body: formData });
        if (response.ok) {
            const result = await response.json();
            videoUrl = result.url;
        }
    }
    
    const requestData = {
        task_id: parseInt(taskId),
        completed_by: currentUser.user_id,
        notes: notes || "Task completed"
    };
    
    if (photoUrl) requestData.image_url = photoUrl;
    if (audioUrl) requestData.audio_url = audioUrl;
    if (videoUrl) requestData.video_url = videoUrl;
    
    const response = await fetch('/tasks/complete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestData)
    });
    
    if (response.ok) {
        showMessage('Task completed successfully!');
        closeCompletionModal();
        loadTasks();
        if (typeof loadAllTasks === 'function') loadAllTasks();
    } else {
        const error = await response.json();
        showMessage(error.detail || 'Failed to complete task', 'error');
    }
}

async function createTask() {
    const taskData = {
        title: document.getElementById('taskTitle').value,
        description: document.getElementById('taskDesc').value,
        task_type: document.getElementById('taskType').value,
        time_slot: document.getElementById('taskTimeSlot').value,
        location_id: parseInt(document.getElementById('taskLocationId').value),
        zone_id: document.getElementById('taskZoneId').value ? parseInt(document.getElementById('taskZoneId').value) : null,
        assigned_to: parseInt(document.getElementById('taskAssignedTo').value),
        created_by: currentUser.user_id
    };
    
    const response = await fetch('/tasks/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(taskData)
    });
    
    if (response.ok) {
        showMessage('Task created successfully!');
        document.getElementById('taskTitle').value = '';
        document.getElementById('taskDesc').value = '';
        loadTasks();
    } else {
        showMessage('Failed to create task', 'error');
    }
}

async function createLocation() {
    const locationData = {
        name: document.getElementById('locationName').value,
        area_acres: parseFloat(document.getElementById('locationArea').value),
        region: document.getElementById('locationRegion').value
    };
    
    const response = await fetch('/locations/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(locationData)
    });
    
    if (response.ok) {
        showMessage('Location added successfully!');
        document.getElementById('locationName').value = '';
        loadLocations();
    } else {
        showMessage('Failed to add location', 'error');
    }
}

async function createZone() {
    const locationId = document.getElementById('zoneLocationId').value;
    const zoneName = document.getElementById('zoneName').value;
    const zoneArea = document.getElementById('zoneArea').value;
    
    if (!locationId || !zoneName) {
        showMessage('Please fill all fields', 'error');
        return;
    }
    
    const zoneData = {
        name: zoneName,
        area_acres: parseFloat(zoneArea) || 0,
        location_id: parseInt(locationId)
    };
    
    const response = await fetch('/zones/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(zoneData)
    });
    
    if (response.ok) {
        showMessage('Zone added successfully!');
        document.getElementById('zoneName').value = '';
        document.getElementById('zoneArea').value = '';
        loadAllZones();
    } else {
        showMessage('Failed to add zone', 'error');
    }
}

async function createContact() {
    const contactData = {
        name: document.getElementById('contactName').value,
        phone: document.getElementById('contactPhone').value,
        issue_type: document.getElementById('contactIssueType').value,
        location_id: parseInt(document.getElementById('contactLocationId').value)
    };
    
    const response = await fetch('/contacts/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(contactData)
    });
    
    if (response.ok) {
        showMessage('Contact added successfully!');
        document.getElementById('contactName').value = '';
        document.getElementById('contactPhone').value = '';
    } else {
        showMessage('Failed to add contact', 'error');
    }
}

addUser = async function() {
    const name = document.getElementById('newUserName').value;
    const username = document.getElementById('userUsername').value;
    const password = document.getElementById('userPassword').value;
    const phone = document.getElementById('userPhone').value;
    const role = document.getElementById('newUserRole').value;
    const region = document.getElementById('userRegion').value;
    const language = document.getElementById('userLanguage').value;
    
    if (!name || !username || !password || !role) {
        showMessage('Please fill all fields', 'error');
        return;
    }
    
    const response = await fetch('/add-user', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, username, password, phone, role, region, language })
    });
    
    if (response.ok) {
        showMessage(`User ${name} added successfully!`);
        document.getElementById('newUserName').value = '';
        document.getElementById('userUsername').value = '';
        document.getElementById('userPassword').value = '';
        document.getElementById('userPhone').value = '';
        loadAllUsers();
    } else {
        showMessage('Failed to add user', 'error');
    }
}

function logout() {
    currentUser = null;
    document.getElementById("loginSection").classList.add("active");
    document.getElementById("appSection").classList.remove("active");
    document.getElementById("bottomNav").style.display = "none";
    showMessage("Logged out successfully");
}

function reportIssue() {
    const locationId = document.getElementById("issueLocation").value;
    if (!locationId) {
        showMessage("Please select a location", "error");
        return;
    }
    showMessage("Issue reported! (API coming soon)", "success");
    document.getElementById("issueDescription").value = "";
}