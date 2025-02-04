document.querySelectorAll('.edit-score-btn').forEach(button => {
    button.addEventListener('click', function() {
        let noteId = this.dataset.noteId;
        document.getElementById('editScoreModal').style.display = 'block';
        document.getElementById('saveScoreBtn').setAttribute('data-note-id', noteId);
    });
});

// Close the popup when clicking the "×" button
document.querySelector('.close').addEventListener('click', function() {
    document.getElementById('editScoreModal').style.display = 'none';
});

// Close the popup when clicking outside of it
window.addEventListener('click', function(event) {
    let modal = document.getElementById('editScoreModal');
    if (event.target === modal) {
        modal.style.display = 'none';
    }
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
function openParametersModal() {
    document.getElementById("parametersModal").style.display = "block";
}

function closeParametersModal() {
    document.getElementById("parametersModal").style.display = "none";
}

async function updateCredentials() {
    let oldPassword = document.getElementById("old_password").value;
    let oldSecret = document.getElementById("old_secret").value;
    let newPassword = document.getElementById("new_password").value;
    let newSecret = document.getElementById("new_secret").value;

    if (!oldPassword || !oldSecret || !newPassword || !newSecret) {
        alert("Tous les champs doivent être remplis.");
        return;
    }

    let response = await fetch("/update_credentials", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            old_password: oldPassword,
            old_secret: oldSecret,
            new_password: newPassword,
            new_secret: newSecret
        })
    });

    let result = await response.json();
    if (result.success) {
        alert("Identifiants mis à jour avec succès.");
        closeParametersModal();
    } else {
        alert("Erreur : " + result.error);
    }
}