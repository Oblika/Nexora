// Funksioni për të kërkuar një paketë bazuar në numrin e saj
async function kerkoPaketen() {
    const numriPaketes = document.getElementById('searchInput').value.trim();
    console.log('ID-ja e futur:', numriPaketes); // Debug
    if (!numriPaketes) {
        alert('Ju lutem, shkruani një numër të paketës.');
        return;
    }
    try {
        const response = await fetch(`http://localhost:5000/paketat/${numriPaketes}`);
        console.log('Statusi i përgjigjes:', response.status); // Debug
        if (!response.ok) {
            const errorData = await response.json();
            console.log('Përgjigjja e gabimit:', errorData); // Debug
            throw new Error(errorData.message || 'Pakoja nuk u gjet!');
        }
        const data = await response.json();
        console.log('Të dhënat nga serveri:', data); // Debug
        if (!data || !data.numriPaketes) {
            throw new Error('Të dhënat e pakës janë të pavlefshme!');
        }
        localStorage.setItem('paketadb', JSON.stringify(data));
        window.location.href = '../html/Paketat.html';
    } catch (error) {
        console.error('Gabim gjatë thirrjes së API-së:', error.message);
        alert(error.message);
    }
}
// Funksioni për të shfaqur rezultatet e paketës
function shfaqRezultatet(data) {
    const rezultati = document.getElementById('dataTable');
    const tbody = rezultati.querySelector('tbody') || document.createElement('tbody');
    tbody.innerHTML = ''; // Pastron tabelën nga të dhënat e mëparshme

    if (!rezultati.querySelector('tbody')) {
        rezultati.appendChild(tbody);
    }

    // Mund të shtoni logjikë për të shfaqur të dhënat e paketës këtu
}

// Event listener për ngarkimin e të dhënave nga LocalStorage kur faqja ngarkohet
document.addEventListener('DOMContentLoaded', function () {
    // Merr të dhënat nga LocalStorage
    const paketaData = JSON.parse(localStorage.getItem('paketadb'));

    if (paketaData) {
        // Shfaq të dhënat në tabelë
        const tableBody = document.getElementById('tableBody');
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${paketaData.numriPaketes}</td>
            <td>${paketaData.emriDerguesit}</td>
            <td>${paketaData.kohaArdhjes}</td>
            <td>${paketaData.vendodhjaPakos}</td>
            <td>${paketaData.email}</td>
            <td>${paketaData.adresa}</td>
        `;
        tableBody.appendChild(tr);

        // Shfaq emrin e marrësit në krye
        document.getElementById('emriMarresit').textContent = paketaData.emriMarresit;
    } else {
        alert('Nuk ka të dhëna për t’u shfaqur!');
    }

    // Event listener për butonin e rifreskimit
    document.getElementById('refreshButton').addEventListener('click', function () {
        window.location.href = '../html/index.html'; // Ridrejton në faqen kryesore
    });
});

// Funksioni për menaxhimin e login-it dhe ridrejtimin sipas rolit
document.querySelector("form").addEventListener("submit", async function(event) {
    event.preventDefault();

    const role = document.getElementById("role").value;
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    try {
        console.log("Po dërgohet kërkesa me këto të dhëna:", { role, username, password });

        const response = await fetch('http://localhost:5000/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password, role }), // Kërkesa POST
        });

        const data = await response.json();

        if (response.ok && data.redirect) {
            console.log("Ridrejtimi në:", data.redirect);
            window.location.href = data.redirect; // Ridrejtim në faqen përkatëse
        } else {
            console.error("Mesazh nga serveri:", data.message);
            alert(data.message); // Shfaq mesazhin e gabimit nga serveri
        }
    } catch (error) {
        console.error("Gabim gjatë dërgimit të kërkesës:", error.message);
        alert("Diçka shkoi keq! Ju lutemi, kontrolloni dhe provoni përsëri.");
    }
});


/*  ---------------------- Faqja e Korrierit -------------------------------------       */

function searchPackage() {
    const query = document.getElementById("searchInput").value;

    if (!query) {
      alert("Ju lutem, shkruani një ID të paketës!"); // Kontrollo për input bosh
      return;
    }

    fetch(`http://localhost:5000/api/package/${query}`)
      .then(response => {
        if (!response.ok) {
          throw new Error("Pakoja nuk u gjet ose ka ndodhur një gabim.");
        }
        return response.json();
      })
      .then(data => {
        const tableBody = document.getElementById("tableBody");
        tableBody.innerHTML = ""; // Pastroni përmbajtjen ekzistuese të tabelës

        // Sigurohu që JSON ka të dhëna valide
        if (data.numriPaketes) {
          const row = document.createElement("tr");
          row.innerHTML = `
            <td>${data.numriPaketes}</td>
            <td>${data.emriDerguesit || "N/A"}</td>
            <td>${data.kohaArdhjes || "N/A"}</td>
            <td>${data.vendodhjaPakos || "N/A"}</td>
            <td>${data.email || "N/A"}</td>
            <td>${data.adresa || "N/A"}</td>
          `;
          tableBody.appendChild(row); // Shto rreshtin në tabelë
        } else {
          alert("Pakoja nuk u gjet."); // Njoftim nëse të dhënat janë bosh
        }
      })
      .catch(error => {
        console.error(error); // Shfaq gabime në console
        alert(error.message); // Trego mesazhin e gabimit
      });
  }


