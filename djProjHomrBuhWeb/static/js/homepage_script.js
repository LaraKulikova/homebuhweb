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
    const dateElement = document.getElementById('currency-date');
    const today = new Date();
    const formattedDate = today.toLocaleDateString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
    });
    dateElement.textContent = formattedDate;

    fetchCurrencyRates();

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

    fetch('/api/currency-rates/')
        .then(response => response.json())
        .then(data => {
            const tableBody = document.querySelector('#currency-rates tbody');
            tableBody.innerHTML = '';
            for (const [currency, rate] of Object.entries(data)) {
                const row = document.createElement('tr');
                row.innerHTML = `<td>${currency}</td><td>${rate}</td>`;
                tableBody.appendChild(row);
            }

// Сохранение курсов валют для дальнейшего использования
            document.getElementById('usd-rate').textContent = data.USD;
            document.getElementById('eur-rate').textContent = data.EUR;
            document.getElementById('rub-rate').textContent = data.RUB;
        })
        .catch(error => console.error('Error fetching currency rates:', error));

    const form = document.querySelector('form');
    form.addEventListener('submit', function (event) {
        event.preventDefault();
        calculateAndSave();
    });

    function calculateAndSave() {
        const creditAmount = parseFloat(document.getElementById('id_credit_amount').value);
        const interestRate = parseFloat(document.getElementById('id_interest_rate').value) / 100;
        const creditTerm = parseInt(document.getElementById('id_credit_term').value);

        if (isNaN(creditAmount) || isNaN(interestRate) || isNaN(creditTerm)) {
            alert('Пожалуйста, введите корректные значения для суммы кредита, срока и процентной ставки.');
            return;
        }

        const monthlyInterest = (creditAmount * interestRate) / 12;
        const monthlyPayment = (creditAmount / creditTerm) + monthlyInterest;

// Обновление суммы всех платежей в месяц
        let totalMonthlyPayments = parseFloat(document.querySelector('.total-monthly-payments').textContent.match(/[\d.]+/)[0]);
        totalMonthlyPayments += monthlyPayment;

        document.querySelector('.total-monthly-payments').textContent = 'Примерная сумма платежей по кредитам в месяц: ' + totalMonthlyPayments.toFixed(2) + ' BYN';

// Асинхронный запрос для обновления данных на сервере
        fetch('/update_total_monthly_payments/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({total_monthly_payments: totalMonthlyPayments.toFixed(2)})
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Ошибка сети');
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    form.submit();
                } else {
                    alert('Ошибка при обновлении суммы всех платежей.');
                }
            })
            .catch(error => {
                console.error('Ошибка:', error);
                alert('Произошла ошибка при обновлении суммы всех платежей. Пожалуйста, попробуйте позже.');
            });
    }

// Логика для планируемых расходов
    const plannedExpensesForm = document.getElementById('planned-expenses-form');
    plannedExpensesForm.addEventListener('submit', function (event) {
        event.preventDefault();
        calculateAndSavePlannedExpenses();
    });

    function calculateAndSavePlannedExpenses() {
        const plannedAmount = parseFloat(document.getElementById('id_planned_amount').value);
        const usdRate = parseFloat(document.getElementById('usd-rate').textContent);
        const eurRate = parseFloat(document.getElementById('eur-rate').textContent);
        const rubRate = parseFloat(document.getElementById('rub-rate').textContent);

        const plannedAmountUSD = plannedAmount / usdRate;
        const plannedAmountEUR = plannedAmount / eurRate;
        const plannedAmountRUB = plannedAmount / rubRate;

        if (isNaN(plannedAmount)) {
            alert('Пожалуйста, введите корректное значение для планируемых расходов.');
            return;
        }

// Обновление суммы планируемых расходов в месяц
        let totalPlannedExpenses = parseFloat(document.querySelector('.planned-expenses').textContent.match(/[\d.]+/)[0]);
        totalPlannedExpenses += plannedAmount;

        document.querySelector('.planned-expenses').textContent = 'Сумма планируемых расходов в месяц: ' + totalPlannedExpenses.toFixed(2) + ' BYN (' + plannedAmountUSD.toFixed(2) + ' USD, ' + plannedAmountEUR.toFixed(2) + ' EUR, ' + plannedAmountRUB.toFixed(2) + ' RUB)';

// Асинхронный запрос для обновления данных на сервере
        fetch('/update_total_planned_expenses/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                total_planned_expenses: totalPlannedExpenses.toFixed(2),
                total_planned_expenses_usd: plannedAmountUSD.toFixed(2),
                total_planned_expenses_eur: plannedAmountEUR.toFixed(2),
                total_planned_expenses_rub: plannedAmountRUB.toFixed(2)
            })
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Ошибка сети');
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    plannedExpensesForm.submit();
                } else {
                    alert('Ошибка при обновлении суммы планируемых расходов.');
                }
            })
            .catch(error => {
                console.error('Ошибка:', error);
                alert('Произошла ошибка при обновлении суммы планируемых расходов. Пожалуйста, попробуйте позже.');
            });
    }
});

function fetchCurrencyRates() {
    fetch('/get_currency_rates/')
        .then(response => response.json())
        .then(data => {
            const tbody = document.querySelector('#currency-rates tbody');
            tbody.innerHTML = '';
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

// Сохранение курсов валют для дальнейшего использования
            document.getElementById('usd-rate').textContent = data.USD;
            document.getElementById('eur-rate').textContent = data.EUR;
            document.getElementById('rub-rate').textContent = data.RUB;
        })
        .catch(error => console.error('Error fetching currency rates:', error));
}