// ============================================
// MEDIA VIEWER - Complete
// ============================================

function viewMedia(mediaUrl, mediaType) {
    const imageEl = document.getElementById('viewerImage');
    const audioEl = document.getElementById('viewerAudio');
    const videoEl = document.getElementById('viewerVideo');
    const noMediaEl = document.getElementById('noMediaMessage');
    
    imageEl.style.display = 'none';
    audioEl.style.display = 'none';
    videoEl.style.display = 'none';
    noMediaEl.style.display = 'none';
    
    if (!mediaUrl) {
        noMediaEl.style.display = 'block';
        document.getElementById('mediaViewerModal').style.display = 'flex';
        return;
    }
    
    if (mediaType === 'image') {
        imageEl.src = mediaUrl;
        imageEl.style.display = 'block';
    } else if (mediaType === 'audio') {
        audioEl.querySelector('source').src = mediaUrl;
        audioEl.load();
        audioEl.style.display = 'block';
    } else if (mediaType === 'video') {
        videoEl.querySelector('source').src = mediaUrl;
        videoEl.load();
        videoEl.style.display = 'block';
    }
    
    document.getElementById('mediaViewerModal').style.display = 'flex';
}

function closeMediaViewer() {
    document.getElementById('mediaViewerModal').style.display = 'none';
    const audioEl = document.getElementById('viewerAudio');
    const videoEl = document.getElementById('viewerVideo');
    if (audioEl) audioEl.pause();
    if (videoEl) videoEl.pause();
}

function viewLocationLayout(layoutUrl, locationName) {
    const modalHtml = `
        <div id="layoutModal" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.9); z-index: 4000;">
            <div style="position: relative; width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; flex-direction: column;">
                <button onclick="closeLayoutModal()" style="position: absolute; top: 20px; right: 20px; background: red; color: white; border: none; border-radius: 50%; width: 40px; height: 40px; font-size: 20px; cursor: pointer;">✕</button>
                <h3 style="color: white; margin-bottom: 20px;">${locationName} - Layout Map</h3>
                <img src="${layoutUrl}" style="max-width: 90%; max-height: 80%; object-fit: contain; border: 2px solid white; border-radius: 8px;">
                <p style="color: white; margin-top: 20px;">Click the X button or press ESC to close</p>
            </div>
        </div>
    `;
    
    if (!document.getElementById('layoutModal')) {
        document.body.insertAdjacentHTML('beforeend', modalHtml);
    } else {
        const modal = document.getElementById('layoutModal');
        modal.style.display = 'flex';
        modal.querySelector('img').src = layoutUrl;
        modal.querySelector('h3').textContent = `${locationName} - Layout Map`;
    }
    document.getElementById('layoutModal').style.display = 'flex';
}

function closeLayoutModal() {
    const modal = document.getElementById('layoutModal');
    if (modal) modal.style.display = 'none';
}

document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeLayoutModal();
        closeMediaViewer();
    }
});