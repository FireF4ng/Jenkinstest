function openParametersModal() {
    document.getElementById("parametersModal").style.display = "block";
}

function closeParametersModal() {
    document.getElementById("parametersModal").style.display = "none";
}

async function updateCredentials() {
    let oldPassword = document.getElementById("old_password").value;
    let newPassword = document.getElementById("new_password").value;

    if (!oldPassword || !newPassword) {
        alert("Tous les champs doivent être remplis.");
        return;
    }

    let response = await fetch("/update_credentials", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            old_password: oldPassword,
            new_password: newPassword,
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