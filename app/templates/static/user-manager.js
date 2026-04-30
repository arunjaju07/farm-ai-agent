// ============================================
// USER MANAGEMENT - Complete
// ============================================

let editingUserId = null;

async function loadAllUsers() {
    try {
        const response = await fetch('/users');
        if (!response.ok) {
            console.error("Failed to fetch users");
            return;
        }
        
        const users = await response.json();
        const usersDiv = document.getElementById('allUsersList');
        
        if (!usersDiv) {
            console.error("allUsersList element not found");
            return;
        }
        
        if (users.length === 0) {
            usersDiv.innerHTML = '<p style="color: #999;">No users found</p>';
            return;
        }
        
        let html = '<div class="table-container"><table style="width:100%; border-collapse: collapse;">';
        html += '<tr style="background: #f0f0f0;"><th style="padding: 8px;">Name</th><th style="padding: 8px;">Role</th><th style="padding: 8px;">Username</th><th style="padding: 8px;">Region</th><th style="padding: 8px;">Actions</th></tr>';
        
        users.forEach(user => {
            html += `
                <tr style="border-bottom: 1px solid #ddd;">
                    <td style="padding: 8px;">${user.name}</tr>
                    <td style="padding: 8px;">${user.role}</td>
                    <td style="padding: 8px;">${user.username}</td>
                    <td style="padding: 8px;">${user.region || '-'}</td>
                    <td style="padding: 8px;">
                        <button onclick="editUser(${user.id})" style="background: #2196F3; padding: 5px 10px; width: auto; margin-right: 5px;">✏️ Edit</button>
                        <button onclick="deleteUser(${user.id})" style="background: #f44336; padding: 5px 10px; width: auto;">🗑️ Delete</button>
                    </td>
                </tr>
            `;
        });
        html += '</table></div>';
        usersDiv.innerHTML = html;
    } catch (error) {
        console.error("Error loading users:", error);
    }
}

async function addUser() {
    const name = document.getElementById('newUserName').value;
    const username = document.getElementById('userUsername').value;
    const password = document.getElementById('userPassword').value;
    const phone = document.getElementById('userPhone').value;
    const role = document.getElementById('newUserRole').value;
    const region = document.getElementById('userRegion').value;
    const language = document.getElementById('userLanguage').value;
    
    const userData = { name, username, password, phone, role, region, language };
    
    if (!name || !username || !password || !role) {
        showMessage('Please fill all fields', 'error');
        return;
    }
    
    const response = await fetch('/add-user', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userData)
    });
    
    if (response.ok) {
        showMessage(`User ${name} added successfully!`);
        document.getElementById('newUserName').value = '';
        document.getElementById('userUsername').value = '';
        document.getElementById('userPassword').value = '';
        document.getElementById('userPhone').value = '';
        loadAllUsers();
    } else {
        const error = await response.json();
        showMessage(error.detail || 'Failed to add user', 'error');
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
        const error = await response.json();
        showMessage(error.detail || 'Failed to update user', 'error');
    }
}

async function deleteUser(userId) {
    if (confirm('Are you sure you want to delete this user?')) {
        const response = await fetch(`/user/delete/${userId}`, { method: 'DELETE' });
        if (response.ok) {
            showMessage('User deleted successfully!');
            loadAllUsers();
        } else {
            const error = await response.json();
            showMessage(error.detail || 'Failed to delete user', 'error');
        }
    }
}

function closeEditModal() {
    document.getElementById('editUserModal').style.display = 'none';
}