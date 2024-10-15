console.log('homepage_script.js загружен');

function handleRegistration() {
    console.log('handleRegistration вызвана');
    const username = document.getElementById('inputUsername').value;
    const password = document.getElementById('inputPasswordReg').value;
    const passwordConfirm = document.getElementById('inputPasswordConfirm').value;

    if (password !== passwordConfirm) {
        alert('Пароли не совпадают!');
        return;
    }

    console.log('Отправка данных на сервер');
    fetch('/register/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            username: username,
            password: password,
            password_confirm: passwordConfirm
        })
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Ошибка сети');
            }
            return response.json();
        })
        .then(data => {
            console.log('Ответ от сервера:', data);
            if (data.success) {
                alert('Регистрация прошла успешно!');
                location.reload();
            } else {
                alert('Ошибка регистрации: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Ошибка:', error);
            alert('Произошла ошибка при регистрации. Пожалуйста, попробуйте позже.');
        });
}

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
    console.log('DOM полностью загружен и разобран');
    var backToTopButton = document.getElementById('back-to-top');
    if (backToTopButton) {
        console.log('Кнопка "Наверх" найдена');
        backToTopButton.addEventListener('click', function (event) {
            event.preventDefault();
            console.log('Кнопка "Наверх" нажата');
            document.documentElement.scrollIntoView({behavior: 'smooth', block: 'start'});
        });
    } else {
        console.log('Кнопка "Наверх" не найдена');
    }
});

document.addEventListener('DOMContentLoaded', function () {
    fetch('https://www.nbrb.by/api/exrates/rates?periodicity=0')
        .then(response => response.json())
        .then(data => {
            const tableBody = document.querySelector('#currency-rates tbody');
            const currencies = ['USD', 'EUR', 'RUB'];
            data.forEach(rate => {
                if (currencies.includes(rate.Cur_Abbreviation)) {
                    const row = document.createElement('tr');
                    const currencyCell = document.createElement('td');
                    currencyCell.textContent = rate.Cur_Abbreviation;
                    currencyCell.style.backgroundColor = '#A78B71';
                    currencyCell.style.color = '#fff';
                    const rateCell = document.createElement('td');
                    rateCell.textContent = rate.Cur_OfficialRate;
                    rateCell.style.backgroundColor = '#A78B71';
                    rateCell.style.color = '#fff';
                    row.appendChild(currencyCell);
                    row.appendChild(rateCell);
                    tableBody.appendChild(row);
                }
            });
        })
        .catch(error => console.error('Ошибка при загрузке данных:', error));
});