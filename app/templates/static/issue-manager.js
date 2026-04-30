// ============================================
// ISSUE MANAGEMENT - Complete
// ============================================

async function loadAllIssues() {
    try {
        const response = await fetch('/issues/all');
        const issues = await response.json();
        const container = document.getElementById('allIssuesList');
        
        if (!container) return;
        
        if (issues.length === 0) {
            container.innerHTML = '<p style="color: #999;">No issues reported yet</p>';
            return;
        }
        
        const usersRes = await fetch('/users');
        const users = await usersRes.json();
        const locationsRes = await fetch('/locations/all');
        const locations = await locationsRes.json();
        
        let html = '<div class="table-container"><table style="width:100%; border-collapse: collapse;">';
        html += '<tr style="background: #f0f0f0;"><th>ID</th><th>Type</th><th>Location</th><th>Description</th><th>Reported By</th><th>Status</th><th>Media</th><th>Reported At</th><th>Actions</th></tr>';
        
        for (const issue of issues) {
            const location = locations.find(l => l.id === issue.location_id);
            const locationName = location ? location.name : 'Unknown';
            const reporter = users.find(u => u.id === issue.reported_by);
            const reporterName = reporter ? reporter.name : 'Unknown';
            const statusColor = issue.status === 'resolved' ? '#4CAF50' : (issue.status === 'in_progress' ? '#ff9800' : '#f44336');
            
            let mediaButtons = '';
            if (issue.photo_url) mediaButtons += `<button onclick="viewMedia('${issue.photo_url}', 'image')" style="background: #2196F3; padding: 3px 8px; width: auto; font-size: 10px;">📷 Photo</button>`;
            if (issue.audio_url) mediaButtons += `<button onclick="viewMedia('${issue.audio_url}', 'audio')" style="background: #9c27b0; padding: 3px 8px; width: auto; font-size: 10px;">🎧 Audio</button>`;
            if (issue.video_url) mediaButtons += `<button onclick="viewMedia('${issue.video_url}', 'video')" style="background: #e91e63; padding: 3px 8px; width: auto; font-size: 10px;">🎥 Video</button>`;
            if (mediaButtons === '') mediaButtons = '-';
            
            html += `
                <tr>
                    <td>${issue.id}</td>
                    <td><strong>${issue.issue_type}</strong></td>
                    <td>${locationName}</td>
                    <td>${issue.description || '-'}</td>
                    <td>${reporterName}</td>
                    <td><span style="background: ${statusColor}; color: white; padding: 2px 8px; border-radius: 10px;">${issue.status}</span></td>
                    <td>${mediaButtons}</td>
                    <td>${new Date(issue.created_at).toLocaleString()}</td>
                    <td>
                        <select id="issueStatus_${issue.id}" style="padding: 5px; width: auto;">
                            <option value="pending" ${issue.status === 'pending' ? 'selected' : ''}>Pending</option>
                            <option value="in_progress" ${issue.status === 'in_progress' ? 'selected' : ''}>In Progress</option>
                            <option value="resolved" ${issue.status === 'resolved' ? 'selected' : ''}>Resolved</option>
                        </select>
                        <button onclick="updateIssueStatus(${issue.id})" style="background: #2196F3; padding: 5px 10px; width: auto;">Update</button>
                    </td>
                </tr>
            `;
        }
        html += '</table></div>';
        container.innerHTML = html;
    } catch (error) {
        console.error("Error loading issues:", error);
    }
}

async function updateIssueStatus(issueId) {
    const statusSelect = document.getElementById(`issueStatus_${issueId}`);
    const newStatus = statusSelect.value;
    
    const response = await fetch(`/issues/${issueId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus })
    });
    
    if (response.ok) {
        showMessage('Issue status updated!', 'success');
        loadAllIssues();
    } else {
        showMessage('Failed to update status', 'error');
    }
}

async function reportIssue() {
    const issueType = document.getElementById("issueType").value;
    const locationId = document.getElementById("issueLocation").value;
    const description = document.getElementById("issueDescription").value;
    const photoFile = document.getElementById("issuePhoto").files[0];
    const audioFile = document.getElementById("issueAudio").files[0];
    const videoFile = document.getElementById("issueVideo").files[0];

    if (!locationId) {
        showMessage("Please select a location", "error");
        return;
    }

    showMessage("Uploading media...", "success");

    let photoUrl = null, audioUrl = null, videoUrl = null;

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

    const response = await fetch('/issues/report', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            issue_type: issueType,
            location_id: parseInt(locationId),
            description: description,
            reported_by: currentUser.user_id,
            photo_url: photoUrl,
            audio_url: audioUrl,
            video_url: videoUrl
        })
    });

    if (response.ok) {
        showMessage("Issue reported successfully!", "success");
        document.getElementById("issueDescription").value = "";
        document.getElementById("issueLocation").value = "";
        document.getElementById("issuePhoto").value = "";
        document.getElementById("issueAudio").value = "";
        document.getElementById("issueVideo").value = "";
    } else {
        const error = await response.json();
        showMessage(error.detail || "Failed to report issue", "error");
    }
}