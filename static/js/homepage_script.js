console.log('homepage_script.js загружен');

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function handleLogin() {
    const usernameOrEmail = document.getElementById('inputLogin').value;
    const password = document.getElementById('inputPassword').value;

    fetch('/check_user/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({usernameOrEmail, password})
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Ошибка сети');
            }
            return response.json();
        })
        .then(data => {
            if (data.exists) {
                window.location.href = '/usercabinet/';
            } else {
                alert('Такого пользователя не существует. Проверьте логин и пароль или пройдите регистрацию.');
                $('#loginModal').modal('hide');
            }
        })
        .catch(error => {
            console.error('Ошибка:', error);
            alert('Произошла ошибка при входе в систему. Пожалуйста, попробуйте позже.');
        });
}

document.addEventListener('DOMContentLoaded', function () {
    const categorySelect = document.getElementById('id_category');
    const subcategorySelect = document.getElementById('id_subcategory');
    const subsubcategorySelect = document.getElementById('id_subsubcategory');

    categorySelect.addEventListener('change', function () {
        const categoryId = this.value;
        fetch(`/get_subcategories/${categoryId}/`)
            .then(response => response.json())
            .then(data => {
                subcategorySelect.innerHTML = '<option value="">Выбрать подкатегорию</option>';
                data.forEach(subcategory => {
                    subcategorySelect.innerHTML += `<option value="${subcategory.id}">${subcategory.name}</option>`;
                });
                subsubcategorySelect.innerHTML = '<option value="">Выбрать подподкатегорию</option>'; // Очистить подподкатегории
            });
    });

    subcategorySelect.addEventListener('change', function () {
        const subcategoryId = this.value;
        fetch(`/get_subsubcategories/${subcategoryId}/`)
            .then(response => response.json())
            .then(data => {
                subsubcategorySelect.innerHTML = '<option value="">Выбрать подподкатегорию</option>';
                data.forEach(subsubcategory => {
                    subsubcategorySelect.innerHTML += `<option value="${subsubcategory.id}">${subsubcategory.name}</option>`;
                });
            });
    });
});

document.addEventListener('DOMContentLoaded', function() {
fetchCurrencyRates();
});

function fetchCurrencyRates() {
fetch('/api/currency-rates/')
.then(response => response.json())
.then(data => {
const tbody = document.querySelector('#currency-rates tbody');
tbody.innerHTML = ''; // Очистить существующие строки
for (const [currency, rate] of Object.entries(data)) {
const row = document.createElement('tr');
const currencyCell = document.createElement('td');
const rateCell = document.createElement('td');
currencyCell.textContent = currency;
rateCell.textContent = rate;
row.appendChild(currencyCell);
row.appendChild(rateCell);
tbody.appendChild(row);
}
})
.catch(error => console.error('Ошибка при получении курсов валют:', error));
}
//курсы валют
console.log('homepage_script.js загружен');

    document.addEventListener('DOMContentLoaded', function () {
        fetchCurrencyRates();
    });

    function fetchCurrencyRates() {
        fetch('https://www.nbrb.by/api/exrates/rates?periodicity=0')
            .then(response => response.json())
            .then(data => {
                const tbody = document.querySelector('#currency-rates tbody');
                tbody.innerHTML = ''; // Очистить существующие строки
                data.forEach(rate => {
                    if (['USD', 'EUR', 'RUB'].includes(rate.Cur_Abbreviation)) {
                        const row = document.createElement('tr');
                        const currencyCell = document.createElement('td');
                        const rateCell = document.createElement('td');
                        currencyCell.textContent = rate.Cur_Abbreviation;
                        rateCell.textContent = rate.Cur_OfficialRate;
                        row.appendChild(currencyCell);
                        row.appendChild(rateCell);
                        tbody.appendChild(row);
                    }
                });
            })
            .catch(error => console.error('Ошибка при получении курсов валют:', error));
    }