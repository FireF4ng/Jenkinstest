function openParametersModal() {
    document.getElementById("parametersModal").style.display = "block";
}

function closeParametersModal() {
    document.getElementById("parametersModal").style.display = "none";
}

async function updateCredentials() {
    console.log("🟢 Bouton cliqué, tentative d'envoi du formulaire...");

    const oldPassword = document.getElementById('old_password').value;
    const newPassword = document.getElementById('new_password').value;
    const csrfToken = document.querySelector('[name="csrf_token"]').value;

    console.log("🔵 Données envoyées :", { old_password: oldPassword, new_password: newPassword, csrf_token: csrfToken });

    const response = await fetch('/update_credentials', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
            old_password: oldPassword,
            new_password: newPassword,
        })
    });

    console.log("🟡 Réponse reçue :", response);

    const data = await response.json();
    console.log("🟠 Données JSON reçues :", data);

    if (data.success) {
        alert("Mot de passe mis à jour avec succès !");
    } else {
        alert("Erreur: " + data.error);
    }
}

