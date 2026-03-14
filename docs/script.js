let repos = [];
let currentPage = 1;
const itemsPerPage = 25;

fetch('repos.json')
    .then(r => r.json())
    .then(data => {
        repos = data;
        renderTable();
    });

function renderTable() {
    const start = (currentPage - 1) * itemsPerPage;
    const end = start + itemsPerPage;
    const pageRepos = repos.slice(start, end);

    const tbody = document.getElementById('repoTableBody');
    tbody.innerHTML = pageRepos.map((r, i) => `
        <tr>
            <td>${start + i + 1}</td>
            <td>${r.category}</td>
            <td>${r.name}</td>
            <td>${r.stars.toLocaleString()}</td>
            <td>${r.ss}</td>
            <td>${r.language}</td>
        </tr>
    `).join('');

    const totalPages = Math.ceil(repos.length / itemsPerPage);
    const info = `Page ${currentPage} of ${totalPages} (${repos.length} total)`;
    document.getElementById('pageInfo').textContent = info;
    document.getElementById('pageInfo2').textContent = info;

    document.getElementById('prevBtn').disabled = currentPage === 1;
    document.querySelectorAll('button[onclick="changePage(1)"]').forEach(b =>
        b.disabled = currentPage === totalPages
    );
}

function changePage(delta) {
    const totalPages = Math.ceil(repos.length / itemsPerPage);
    currentPage = Math.max(1, Math.min(totalPages, currentPage + delta));
    renderTable();
    document.querySelector('.examples').scrollIntoView({ behavior: 'smooth' });
}
