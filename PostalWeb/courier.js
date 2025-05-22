// Kur DOM ngarkohet plotësisht
document.addEventListener('DOMContentLoaded', () => {
    const searchButton = document.getElementById('searchButton');
    const searchInput = document.getElementById('searchInput');

    searchButton.addEventListener('click', searchPaketa);

    searchInput.addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            event.preventDefault();
            searchPaketa();
        }
    });
});

// Funksioni që bën kërkimin e paketës
function searchPaketa() {
    const searchInput = document.getElementById('searchInput');
    const searchValue = searchInput.value.trim();

    if (!searchValue) {
        triggerShake(searchInput); // Efekti shake nëse input-i është bosh
        Swal.fire({
            icon: 'warning',
            title: 'Kujdes!',
            text: 'Ju lutem shkruani një numër pakete!',
            confirmButtonColor: '#d33',
            confirmButtonText: 'OK'
        });
        return;
    }

    fetch(`http://localhost:5000/search?search=${encodeURIComponent(searchValue)}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP gabim! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(pkg => {
            const tbody = document.getElementById('courierPaketatBody');
            tbody.innerHTML = '';

            if (!pkg || Object.keys(pkg).length === 0) {
                tbody.innerHTML = '<tr><td colspan="7">Asnjë paketë nuk u gjet</td></tr>';
                Swal.fire({
                    icon: 'warning',
                    title: 'Nuk u gjet!',
                    text: 'Asnjë paketë nuk u gjet!',
                    confirmButtonColor: '#d33',
                    confirmButtonText: 'Kuptova'
                });
            } else {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td><input type="text" value="${pkg.numriPaketes || ''}" readonly></td>
                    <td><input type="text" value="${pkg.emriDerguesit || ''}" readonly></td>
                    <td><input type="text" value="${pkg.kohaArdhjes || ''}" readonly></td>
                    <td><input type="text" value="${pkg.vendodhjaPakos || ''}" id="location_${pkg.numriPaketes}" onchange="updateLocation('${pkg.numriPaketes}')"></td>
                    <td><input type="text" value="${pkg.emriMarresit || ''}" readonly></td>
                    <td><input type="text" value="${pkg.email || ''}" readonly></td>
                    <td><input type="text" value="${pkg.adresa || ''}" readonly></td>
                `;
                tbody.appendChild(row);

                Swal.fire({
                    icon: 'success',
                    title: 'Sukses!',
                    text: 'Paketa u shfaq në tabelë!',
                    timer: 2000,
                    timerProgressBar: true,
                    showConfirmButton: false
                });

                // Efekti smooth scroll për të lëvizur tek tabela pas shfaqjes së paketës
                tbody.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }

            clearInputWithPulse(searchInput); // Efekt pulse kur shfaqet paketa
        })
        .catch(error => {
            console.error('Gabim gjatë kërkimit:', error.message);
            Swal.fire({
                icon: 'error',
                title: 'Gabim!',
                text: 'Gabim gjatë kërkimit: ' + error.message,
                confirmButtonColor: '#d33',
                confirmButtonText: 'Kuptova'
            });
            clearInputWithPulse(searchInput); // Edhe në error, efekti
        });
}

// Funksioni për të përditësuar vendodhjen e paketës
function updateLocation(numriPaketes) {
    const locationInput = document.getElementById(`location_${numriPaketes}`);
    if (!locationInput) {
        Swal.fire({
            icon: 'error',
            title: 'Gabim!',
            text: 'Fusha e vendodhjes nuk u gjet!',
            confirmButtonColor: '#d33',
            confirmButtonText: 'Kuptova'
        });
        return;
    }
    const newLocation = locationInput.value;

    const formData = new FormData();
    formData.append('numriPaketes', numriPaketes);
    formData.append('location', newLocation);

    fetch('http://localhost:5000/update_location', {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                Swal.fire({
                    icon: 'success',
                    title: 'U përditësua!',
                    text: 'Vendodhja e paketës u ndryshua me sukses!',
                    timer: 2000,
                    timerProgressBar: true,
                    showConfirmButton: false
                });
            } else {
                Swal.fire({
                    icon: 'error',
                    title: 'Gabim!',
                    text: 'Gabim gjatë përditësimit: ' + data.error,
                    confirmButtonColor: '#d33',
                    confirmButtonText: 'Kuptova'
                });
            }
        })
        .catch(error => {
            console.error('Gabim gjatë përditësimit:', error.message);
            Swal.fire({
                icon: 'error',
                title: 'Gabim!',
                text: 'Gabim gjatë përditësimit: ' + error.message,
                confirmButtonColor: '#d33',
                confirmButtonText: 'Kuptova'
            });
        });
}

// Funksioni për efekt "pulse" kur pastrohet inputi
function clearInputWithPulse(inputElement) {
    inputElement.value = '';
    inputElement.classList.add('pulse');

    setTimeout(() => {
        inputElement.classList.remove('pulse');
    }, 1000);
}

// Funksioni për efekt "shake" kur ka gabim
function triggerShake(inputElement) {
    inputElement.classList.add('shake');

    setTimeout(() => {
        inputElement.classList.remove('shake');
    }, 500);
}
// Dergimi i SMS

