// ============================================
// AUTHENTICATION - Login/Logout
// ============================================

// DON'T declare currentUser here - it's already declared in index.html

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
            currentUser = await response.json();  // Just assign, don't declare
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
                    if (typeof loadAllTasks === 'function') loadAllTasks();
                } else {
                    quickActionsCard.style.display = "block";
                    showSection('tasks');
                }
            }

            if (typeof loadLocations === 'function') loadLocations();
            if (typeof loadTasks === 'function') loadTasks();
            if (typeof loadLocationsForDropdowns === 'function') loadLocationsForDropdowns();
            
        } else {
            const error = await response.json();
            showMessage(error.detail || "Login failed", "error");
        }
    } catch (err) {
        showMessage("Network error. Is the server running?", "error");
    }
}

function logout() {
    currentUser = null;
    document.getElementById("loginSection").classList.add("active");
    document.getElementById("appSection").classList.remove("active");
    document.getElementById("bottomNav").style.display = "none";
    showMessage("Logged out successfully");
}

function showSection(sectionName) {
    if (sectionName === 'admin' && currentUser?.role === 'worker') { 
        showMessage("Access denied", "error"); 
        return; 
    }
    
    const sections = ['tasksSection', 'locationsSection', 'reportIssueSection', 'adminSection'];
    sections.forEach(section => {
        const el = document.getElementById(section);
        if (el) el.classList.remove("active");
    });

    const targetSection = document.getElementById(`${sectionName}Section`);
    if (targetSection) targetSection.classList.add("active");
    
    if (sectionName === "locations" && typeof loadLocations === 'function') loadLocations();
    if (sectionName === "reportIssue" && typeof loadLocations === 'function') loadLocations();
    if (sectionName === "tasks" && typeof loadTasks === 'function') loadTasks();

    if (sectionName === "admin") {
        if (currentUser?.role !== "admin" && currentUser?.role !== "supervisor") {
            showMessage("Access denied. Admin or Supervisor only.", "error");
            return;
        }
        if (typeof loadAllUsers === 'function') loadAllUsers();
        if (typeof loadLocationsForDropdowns === 'function') loadLocationsForDropdowns();
        if (typeof loadAllTasks === 'function') loadAllTasks();
        if (typeof loadAllIssues === 'function') loadAllIssues();
    }
}