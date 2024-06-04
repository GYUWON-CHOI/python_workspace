document.addEventListener('DOMContentLoaded', () => {
    const searchForm = document.getElementById('searchForm');
    const searchInput = document.getElementById('searchInput');
    
    searchForm.addEventListener('submit', (event) => {
        event.preventDefault();
        const query = searchInput.value.trim();
        if (query) {
            alert(`검색어: ${query}`);
            // 실제 검색 기능을 구현하려면 이곳에 추가
        } else {
            alert('검색어를 입력하세요.');
        }
    });
});
