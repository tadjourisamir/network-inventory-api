// Chargement automatique des équipements dans le tableau
document.addEventListener('DOMContentLoaded', () => {
  fetch('/equipements')
    .then(response => response.json())
    .then(data => {
      const tableBody = document.querySelector('#equipTable tbody');

      if (data.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="8">No equipment found.</td></tr>';
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
          <td>
            <button class="delete-btn" data-id="${equipement.id}">🗑️</button>
          </td>
        `;
        tableBody.appendChild(row);
      });

      // Ajouter les handlers de suppression après que les lignes soient dans le DOM
      document.querySelectorAll('.delete-btn').forEach(btn => {
        btn.addEventListener('click', () => {
          const id = btn.dataset.id;
          if (!confirm('❗ Supprimer cet équipement ?')) return;

          fetch(`/equipements/${id}`, {
            method: 'DELETE',
            headers: {
              'x-api-key': 'n4tX7f92Jw92kQeT!sEcReT_k3y'
            }
          })
            .then(res => res.json())
            .then(() => location.reload())
            .catch(err => {
              alert('❌ Échec de la suppression');
              console.error(err);
            });
        });
      });
    })
    .catch(error => {
      console.error('Failed to load equipment:', error);
      const tableBody = document.querySelector('#equipTable tbody');
      tableBody.innerHTML = '<tr><td colspan="8" style="color:red;">Failed to load equipment</td></tr>';
    });
});

// Envoi du formulaire d'ajout d'équipement
document.getElementById('equipForm').addEventListener('submit', function (e) {
  e.preventDefault();

  const form = e.target;
  const message = document.getElementById('formMessage');

  const data = {
    nom: form.nom.value,
    type: form.type.value,
    ip: form.ip.value,
    mac: form.mac.value,
    vlan: form.vlan.value,
    location: form.location.value
  };

  fetch('/equipements', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': 'n4tX7f92Jw92kQeT!sEcReT_k3y'
    },
    body: JSON.stringify(data)
  })
    .then(res => res.json().then(json => ({ status: res.status, body: json })))
    .then(({ status, body }) => {
      if (status === 201) {
        message.style.color = 'green';
        message.textContent = '✅ Equipment added!';
        form.reset();
        location.reload();
      } else {
        message.style.color = 'red';
        message.textContent = '❌ ' + (body.error || 'Unknown error');
      }
    })
    .catch(err => {
      message.style.color = 'red';
      message.textContent = '❌ Request failed';
      console.error(err);
    });
});
