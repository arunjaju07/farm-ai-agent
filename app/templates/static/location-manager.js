// ============================================
// LOCATION & ZONE MANAGEMENT - Complete
// ============================================

async function createLocation() {
    const locationData = {
        name: document.getElementById('locationName').value,
        area_acres: parseFloat(document.getElementById('locationArea').value),
        region: document.getElementById('locationRegion').value,
        layout_url: document.getElementById('locationLayoutUrl').value || null
    };
    
    const response = await fetch('/locations/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(locationData)
    });
    
    if (response.ok) {
        showMessage('Location added successfully!');
        document.getElementById('locationName').value = '';
        document.getElementById('locationArea').value = '';
        document.getElementById('locationLayoutUrl').value = '';
        loadLocations();
        loadLocationsForDropdowns();
    } else {
        showMessage('Failed to add location', 'error');
    }
}

async function createZone() {
    const locationId = document.getElementById('zoneLocationId').value;
    const zoneName = document.getElementById('zoneName').value;
    const zoneArea = document.getElementById('zoneArea').value;
    
    if (!locationId) {
        showMessage('Please select a location', 'error');
        return;
    }
    
    if (!zoneName) {
        showMessage('Please enter zone name', 'error');
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
        const error = await response.json();
        showMessage(error.detail || 'Failed to add zone', 'error');
    }
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
        
        let html = '<div class="table-container"><table style="width:100%; border-collapse: collapse;">';
        zones.forEach(zone => {
            html += `
                <tr style="border-bottom: 1px solid #ddd;">
                    <td style="padding: 8px;"><strong>${zone.name}</strong></td>
                    <td style="padding: 8px;">${zone.area_acres || 0} acres</td>
                    <td style="padding: 8px;">Location ID: ${zone.location_id}</td>
                </tr>
            `;
        });
        html += '</table></div>';
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
        const error = await response.json();
        showMessage(error.detail || 'Failed to update zone', 'error');
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
            const error = await response.json();
            showMessage(error.detail || 'Failed to delete zone', 'error');
        }
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

async function loadLocationsForDropdowns() {
    const response = await fetch('/locations/all');
    if (response.ok) {
        const locations = await response.json();
        
        const selects = ['zoneLocationId', 'manageZoneLocationId', 'taskLocationId', 'contactLocationId'];
        selects.forEach(selectId => {
            const select = document.getElementById(selectId);
            if (select) {
                select.innerHTML = '<option value="">Select Location</option>';
                locations.forEach(loc => {
                    select.innerHTML += `<option value="${loc.id}">${loc.name} (${loc.region})</option>`;
                });
            }
        });
    }
}