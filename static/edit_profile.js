// 1. 프로필 정보 및 사진 수정하기
async function updateProfile() {
    // 사진을 보내기 위한 특별한 상자(FormData) 준비
    const formData = new FormData();
    
    // 글자 데이터 담기
    formData.append('email', document.getElementById('email').value);
    formData.append('phone_number', document.getElementById('phone_number').value);
    formData.append('bio', document.getElementById('bio').value);

    // 사진 파일 담기
    const fileInput = document.getElementById('profile_image');
    if (fileInput.files.length > 0) {
        formData.append('profile_image', fileInput.files[0]);
    }

    try {
        const response = await fetch('/api/edit_profile', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();
        
        if (result.status === 'success') {
            alert('프로필이 성공적으로 업데이트되었습니다!');
            window.location.href = '/profile';
        }
        else if (result.status === 'invalid_file') {
            // 잘못된 파일 업로드 시 알림 후 프로필 페이지로 이동
            alert(result.message);
            window.location.href = '/profile';
        }
        else {
            alert('수정 실패: ' + result.message);
        }
    } catch (error) {
        alert('서버와 통신 오류가 발생했습니다.');
    }
}

// 2.  회원 탈퇴 기능
async function deleteAccount() {
    // 실수로 누르는 걸 방지하기 위해 한 번 더 물어보기
    if (confirm("정말로 회원 탈퇴를 하시겠습니까?\n모든 데이터와 사진, 소개창이 삭제되며 복구할 수 없습니다.")) {
        try {
            const response = await fetch('/api/delete_account', { method: 'POST' });
            const result = await response.json();
            
            if (result.status === 'success') {
                alert(result.message);
                window.location.href = '/'; // 탈퇴 성공 시 맨 처음 로그인 화면으로 쫓아냄
            } else {
                alert("오류 발생: " + result.message);
            }
        } catch (error) {
            alert('서버와 통신 오류가 발생했습니다.');
        }
    }
}