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
        .then(response => response.json())
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
        .then(response => response.json())
        .then(data => {
            if (data.exists) {
                window.location.href = '/usercabinet/';
            } else {
                alert('Такого пользователя не существует. Проверьте логин и пароль или пройдите регистрацию.');
                $('#loginModal').modal('hide');
            }
        })
        .catch(error => console.error('Error:', error));
}