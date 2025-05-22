

/*----------------------------------------------------------------------------------------------------- */

function loadPaketat(searchQuery = '') {
      // Bën kërkesë GET për të marrë paketat nga serveri
    fetch(`http://localhost:5000/api/paketat?search=${encodeURIComponent(searchQuery)}`)
        .then(response => {
            if (!response.ok) throw new Error('Problem me marrjen e të dhënave');
            return response.json();
        })
        .then(data => {
             // Vendin ku do të shtohen të dhënat në HTML
            const adminPaketatBody = document.getElementById('adminPaketatBody');
            adminPaketatBody.innerHTML = '';

            // Nëse nuk ka të dhëna, printo nje mesazh
            if (data.length === 0) {
                adminPaketatBody.innerHTML = '<tr><td colspan="8">Asnjë rezultat</td></tr>';
                return;
            }

             // Për çdo paketë, krijo një rresht në tabelë
            data.forEach(paketa => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${paketa.numriPaketes}</td>
                    <td>${paketa.emriDerguesit}</td>
                    <td>${paketa.kohaArdhjes}</td>
                    <td>${paketa.vendodhjaPakos}</td>
                    <td>${paketa.emriMarresit}</td>
                    <td>${paketa.email}</td>
                    <td>${paketa.adresa}</td>
                    <td>
                        <button class="deliver-btn" data-id="${paketa.numriPaketes}">Pakoja Dorëzuar</button>
                        <button class="reset-btn" data-id="${paketa.numriPaketes}">Reset</button>
                        <button class="delete-btn" data-id="${paketa.numriPaketes}">Delete</button>
                    </td>
                `;
                // Nëse pakoja është dorëzuar, vendos klasën "delivered"
                if (paketa.eshteDorezuar) {
                    row.classList.add('delivered');
                }
                adminPaketatBody.appendChild(row);
            });

            // Butoni per "Dorëzimin e pakos"
            document.querySelectorAll('.deliver-btn').forEach(button => {
                button.addEventListener('click', function() {
                    const numriPaketes = this.getAttribute('data-id');
                    const row = this.closest('tr');
                    fetch(`http://localhost:5000/api/paketat/deliver/${numriPaketes}`, { method: 'PUT' })
                        .then(response => {
                            if (response.ok) row.classList.add('delivered');
                            else throw new Error('Problem me dorëzimin');
                        })
                        .catch(error => console.error('Gabim:', error));
                });
            });

            // "Reset" – heq statusin e dorëzimit
            document.querySelectorAll('.reset-btn').forEach(button => {
                button.addEventListener('click', function() {
                    const numriPaketes = this.getAttribute('data-id');
                    const row = this.closest('tr');
                    fetch(`http://localhost:5000/api/paketat/reset/${numriPaketes}`, { method: 'PUT' })
                        .then(response => {
                            if (response.ok) row.classList.remove('delivered');
                            else throw new Error('Problem me resetimin');
                        })
                        .catch(error => console.error('Gabim:', error));
                });
            });

            // "Delete" – fshin një paketë nga serveri
            document.querySelectorAll('.delete-btn').forEach(button => {
                button.addEventListener('click', function() {
                    const numriPaketes = this.getAttribute('data-id');
                    const row = this.closest('tr');
                    if (confirm('A je i sigurt që dëshiron ta fshish këtë paketë?')) {
                        fetch(`http://localhost:5000/api/paketat/${numriPaketes}`, { method: 'DELETE' })
                            .then(response => {
                                if (response.ok) row.remove();
                                else throw new Error('Problem me fshirjen');
                            })
                            .catch(error => console.error('Gabim:', error));
                    }
                });
            });
        })
        .catch(error => {
            console.error('Gabim:', error);
            document.getElementById('adminPaketatBody').innerHTML = '<tr><td colspan="8">Gabim gjatë ngarkimit</td></tr>';
        });
}
// ----------------------------------------------------------------------------------------------------------------------------- //


// Funksion për të shtuar paketë të re
function addPaketa() {
    const paketa = {
        numriPaketes: document.getElementById('numriPaketes').value,
        emriDerguesit: document.getElementById('emriDerguesit').value,
        kohaArdhjes: document.getElementById('kohaArdhjes').value,
        vendodhjaPakos: document.getElementById('vendodhjaPakos').value,
        emriMarresit: document.getElementById('emriMarresit').value,
        email: document.getElementById('email').value,
        adresa: document.getElementById('adresa').value,
        eshteDorezuar: false
    };

     // Dërgon të dhënat me POST në server
    fetch('http://localhost:5000/api/paketat', {
        method: 'P// Pas shtimit, pastro fushat dhe rifresko tabelënOST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(paketa)
    })
    .then(response => {
        if (!response.ok) throw new Error('Problem me shtimin e pakos');
        return response.json();
    })
    .then(() => {
        // Pas shtimit, pastro fushat dhe rifresko tabelën
        document.getElementById('numriPaketes').value = '';
        document.getElementById('emriDerguesit').value = '';
        document.getElementById('kohaArdhjes').value = '';
        document.getElementById('vendodhjaPakos').value = '';
        document.getElementById('emriMarresit').value = '';
        document.getElementById('email').value = '';
        document.getElementById('adresa').value = '';
        loadPaketat();
    })
    .catch(error => {
        console.error('Gabim:', error);
        alert('Gabim gjatë shtimit të pakos');
    });
}

// ------------------------------------------------------------------------------------------------------------ //

// Funksion për kërkim e pakos sipas numrit
function searchPaketa() {
    const numriPaketes = document.getElementById('searchInput').value.trim();
    loadPaketat(numriPaketes);
}

// Ngarko paketat dhe lidh butonat kur faqja hapet
document.addEventListener('DOMContentLoaded', () => {
    loadPaketat();
    document.getElementById('addPaketaBtn').addEventListener('click', addPaketa);
    document.getElementById('searchInput').addEventListener('input', searchPaketa);
});


// Existing search function (unchanged)
function searchPaketa() {
    const numriPaketes = document.getElementById('searchInput').value.trim();
    loadPaketat(numriPaketes);
}

// Existing DOMContentLoaded event (modified slightly)
document.addEventListener('DOMContentLoaded', () => {
    loadPaketat();
    document.getElementById('addPaketaBtn').addEventListener('click', addPaketa);
    // Keep the input listener if you want live search as user types
    document.getElementById('searchInput').addEventListener('input', searchPaketa);
});


function showTable(tableId) {
        // Fshih të dyja tabelat
        document.getElementById('table1').style.display = 'none';
        document.getElementById('table2').style.display = 'none';

        // Shfaq vetëm atë që është zgjedhur
        document.getElementById(tableId).style.display = 'block';

        // Menaxho stilin aktiv të butonave
        const buttons = document.querySelectorAll('.tab-button');
        buttons.forEach(btn => btn.classList.remove('active'));

        if (tableId === 'table1') {
          buttons[0].classList.add('active');
        } else {
          buttons[1].classList.add('active');
        }
      }

      // Shfaq tabelën e parë kur ngarkohet faqja
      window.onload = function () {
        showTable('table1');
      };