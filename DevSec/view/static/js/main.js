document.querySelectorAll('.edit-score-btn').forEach(button => {
    button.addEventListener('click', function() {
        let noteId = this.dataset.noteId;
        document.getElementById('editScoreModal').style.display = 'block';
        document.getElementById('saveScoreBtn').setAttribute('data-note-id', noteId);
    });
});

// Close the popup when clicking the "×" button
document.querySelectorAll('.close').forEach(button => {
    button.addEventListener('click', function() {
        document.getElementById('editScoreModal').style.display = 'none';
    });
});


// Handle saving new score
document.getElementById('saveScoreBtn').addEventListener('click', function() {
    let noteId = this.dataset.noteId;
    let newScore = document.getElementById('newScoreInput').value;

    fetch('/update_score', {
        method: 'POST',
        body: new URLSearchParams({ note_id: noteId, new_score: newScore }),
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert('Erreur: ' + data.error);
        }
    });
});