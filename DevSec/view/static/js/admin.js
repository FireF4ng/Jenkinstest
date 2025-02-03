document.querySelectorAll('.list-group-item').forEach(item => {
    item.addEventListener('click', function (e) {
        e.preventDefault();
        const table = this.dataset.table;
        loadTableData(table);
    });
});

document.getElementById('add-new').addEventListener('click', () => {
    const activeItem = document.querySelector('.list-group-item.active');
    if (!activeItem) {
        alert("Veuillez d'abord sélectionner une table !");
        return;
    }
    const table = activeItem.dataset.table;
    loadAddForm(table);
});

async function loadTableData(table, searchQuery = "", sortBy = "", sortOrder = "asc") {
    const response = await fetch(`/admin/data?table=${table}&search=${searchQuery}&sort=${sortBy}&order=${sortOrder}`);
    const data = await response.json();

    let html = `<input type="text" id="search-input" class="form-control mb-3" placeholder="Rechercher..." onkeyup="searchTable('${table}')">
                <select id="sort-select" class="form-control mb-3" onchange="sortTable('${table}')">
                    <option value="">Trier par...</option>`;

    if (data.entries.length > 0) {
        Object.keys(data.entries[0]).forEach(col => {
            html += `<option value="${col}">${col}</option>`;
        });
    }
    html += `</select>`;

    html += `<table class="table table-striped table-hover">
                <thead class="table-dark">
                    <tr>`;
    if (data.entries.length > 0) {
        Object.keys(data.entries[0]).forEach(col => {
            html += `<th>${col}</th>`;
        });
        html += `<th>Actions</th>`;
    }
    html += `</tr></thead><tbody>`;

    data.entries.forEach(entry => {
        html += `<tr data-id="${entry.id}" onclick="loadEditForm('${table}', ${entry.id})">`;
        Object.values(entry).forEach(value => {
            html += `<td>${value}</td>`;
        });
        html += `<td>
                    <button class="btn btn-sm btn-danger" onclick="event.stopPropagation(); deleteEntry('${table}', ${entry.id})">Delete</button>
                </td>`;
        html += `</tr>`;
    });

    html += `</tbody></table>`;

    document.getElementById('table-content').innerHTML = html;
    document.getElementById('current-table').textContent = `Editing: ${table}`;
    document.querySelectorAll('.list-group-item').forEach(i => i.classList.remove('active'));
    document.querySelector(`[data-table="${table}"]`).classList.add('active');
}

let searchTimeout;

function searchTable(table) {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
        const query = document.getElementById('search-input').value;
        loadTableData(table, query);
    }, 500);  // Delay of 500ms before refreshing the table
}

function sortTable(table) {
    const sortBy = document.getElementById('sort-select').value;
    const sortOrder = "asc"; // Default to ascending
    loadTableData(table, "", sortBy, sortOrder);
}

async function loadEditForm(table, id) {
    const response = await fetch(`/admin/data?table=${table}&id=${id}`);
    const data = await response.json();

    let formHtml = `<form id="edit-form-${table}" class="edit-form">`;
    Object.entries(data.entry).forEach(([key, value]) => {
        formHtml += `
            <div class="form-group row mb-3">
                <label class="col-sm-3 col-form-label">${key}</label>
                <div class="col-sm-9">
                    <input type="text" class="form-control" name="${key}" value="${value}">
                </div>
            </div>`;
    });
    formHtml += `
        <div class="form-group row">
            <div class="col-sm-9 offset-sm-3">
                <button type="button" class="btn btn-primary" onclick="updateEntry('${table}', ${id})">Save</button>
            </div>
        </div>
    </form>`;

    document.getElementById('edit-form').innerHTML = formHtml;
}

async function loadAddForm(table) {
    const response = await fetch(`/admin/form?table=${table}`);
    const fields = await response.json();

    let formHtml = `<form id="add-form-${table}" class="add-form">`;
    fields.forEach(field => {
        let newValue = field === "id" ? "Auto" : "";
        formHtml += `
            <div class="form-group row mb-3">
                <label class="col-sm-3 col-form-label">${field}</label>
                <div class="col-sm-9">
                    <input type="text" class="form-control" name="${field}" value="${newValue}" ${field === "id" ? "disabled" : ""}>
                </div>
            </div>`;
    });
    formHtml += `
        <div class="form-group row">
            <div class="col-sm-9 offset-sm-3">
                <button type="button" class="btn btn-success" onclick="addEntry('${table}')">Add</button>
            </div>
        </div>
    </form>`;

    document.getElementById('add-modal-body').innerHTML = formHtml;
    new bootstrap.Modal(document.getElementById('addModal')).show();
}

async function addEntry(table) {
    const form = document.getElementById(`add-form-${table}`);
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());

    const response = await fetch(`/admin/add`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({table, data})
    });

    const result = await response.json();
    if (result.success) {
        loadTableData(table);
        bootstrap.Modal.getInstance(document.getElementById('addModal')).hide();
    }
}

async function updateEntry(table, id) {
    const form = document.getElementById(`edit-form-${table}`);
    const formData = new FormData(form);
    const updates = Object.fromEntries(formData.entries());

    const response = await fetch('/admin/update', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({table, id, updates})
    });

    const result = await response.json();
    if (result.success) {
        alert("Entry updated successfully!");
        loadTableData(table);
        document.getElementById('edit-form').innerHTML = '';
    } else {
        alert("Error: " + result.error);
    }
}

async function deleteEntry(table, id) {
    if (!confirm('Are you sure you want to delete this entry?')) return;

    const response = await fetch(`/admin/delete`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({table, id})
    });

    const result = await response.json();
    if (result.success) {
        loadTableData(table);
        document.getElementById('edit-form').innerHTML = '';
    }
}