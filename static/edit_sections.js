// 1. 새 소개창 추가하기
async function addSection() {
    const content = document.getElementById('section_content').value;

    if (!content) {
        alert("내용을 입력해주세요!");
        return;
    }

    try {
        const response = await fetch('/api/add_section', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            // title 없이 content만 백엔드로 보냄
            body: JSON.stringify({ content: content }) 
        });
        
        const result = await response.json();
        if (result.status === 'success') {
            window.location.reload(); 
        } else {
            alert('추가 실패: ' + result.message);
        }
    } catch (error) {
        alert('서버 오류가 발생했습니다.');
    }
}

// 2. 소개창 삭제하기
async function deleteSection(sectionId) {
    if (!confirm("정말로 이 소개창을 삭제하시겠습니까?")) return;

    try {
        const response = await fetch(`/api/delete_section/${sectionId}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        if (result.status === 'success') {
            window.location.reload();
        } else {
            alert('삭제 실패: ' + result.message);
        }
    } catch (error) {
        alert('서버 오류가 발생했습니다.');
    }
}