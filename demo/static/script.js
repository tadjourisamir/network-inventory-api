// Chargement automatique des équipements dans le tableau
document.addEventListener('DOMContentLoaded', () => {
  fetch('/equipements')
    .then(response => response.json())
    .then(data => {
      const tableBody = document.querySelector('#equipTable tbody');

      if (data.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="8">Aucun équipement trouvé.</td></tr>';
        return;
      }

      data.forEach(equipement => {
        const row = document.createElement('tr');
        row.innerHTML = `
          <td>${equipement.id}</td>
          <td>${equipement.nom}</td>
          <td>${equipement.type}</td>
          <td>${equipement.ip}</td>
          <td>${equipement.mac || ''}</td>
          <td>${equipement.vlan || ''}</td>
          <td>${equipement.location || ''}</td>
          <td><em>Lecture seule</em></td>
        `;
        tableBody.appendChild(row);
      });
    })
    .catch(error => {
      console.error('Erreur lors du chargement des équipements :', error);
      const tableBody = document.querySelector('#equipTable tbody');
      tableBody.innerHTML = '<tr><td colspan="8" style="color:red;">Erreur de chargement</td></tr>';
    });
});
