// static/login.js

async function loginUser() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    const data = {
        username: username,
        password: password
    };

    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        const result = await response.json();
        
        if (result.status === 'success') {
            alert('로그인 성공! 환영합니다.');
            window.location.href = '/profile'; // 성공하면 프로필 페이지로 이동!
        } else {
            alert('로그인 실패\n아이디와 비밀번호를 확인해주세요');
            log(result.message)
        }
    } catch (error) {
        alert('서버와 통신하는 중 문제가 발생했습니다.');
    }
}