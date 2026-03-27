async function registerUser() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    // 아이디나 비번을 안 적었을 때 경고 띄우기
    if (!username || !password) {
        alert("아이디와 비밀번호를 모두 입력해주세요!");
        return;
    }

    // ⭐️ 이메일 빼고 아이디랑 비번만 포장!
    const data = {
        username: username,
        password: password
    };

    try {
        const response = await fetch('/api/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (result.status === 'success') {
            alert('회원가입이 완료되었습니다! 로그인해주세요.');
            window.location.href = '/'; // 가입 성공 시 로그인 화면으로 이동
        } else {
            alert('회원가입 실패: ' + result.message);
        }
    } catch (error) {
        alert('서버 통신 오류가 발생했습니다.');
    }
}